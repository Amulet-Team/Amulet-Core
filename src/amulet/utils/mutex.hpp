#pragma once

#include <chrono>
#include <condition_variable>
#include <list>
#include <map>
#include <mutex>
#include <stdexcept>
#include <string>
#include <thread>
#include <tuple>
#include <type_traits>

#include <amulet/dll.hpp>
#include <amulet/utils/task_manager/cancel_manager.hpp>

namespace {

template <template <typename...> class Template, typename T>
struct is_specialization_of : std::false_type { };

template <template <typename...> class Template, typename... Args>
struct is_specialization_of<Template, Template<Args...>> : std::true_type { };

}

namespace Amulet {

class AMULET_CORE_EXPORT_EXCEPTION Deadlock : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
    Deadlock()
        : Deadlock("Deadlock")
    {
    }
};

// This is a custom mutex implementation that can be acquired in:
// 1) Unique mode.
//     - Only one thread can use the resource.
//     - Blocks until no thread holds the mutex
//     - Stops all other threads acquiring the mutex until released.
// 2) Shared read-only mode.
//     - Multiple threads can read (but not write) the resource at the same time.
//     - Can be acquired in parallel with read mode.
//     - Blocks until no thread holds the mutex in unique or write mode.
//     - Stops other threads acquiring in unique and write mode until released.
// 3) Shared read mode.
//     - This thread may only read but other threads may write in parallel.
//     - Only thread-safe functions may be called in this mode.
//     - Can be acquired in parallel with read-only mode or write mode (not at the same time)
//     - Blocks until no thread holds the mutex in unique mode.
//     - Stops other threads acquiring in unique mode until released.
// 4) Shared read-write mode.
//     - This thread may read and write in parallel with other reading and writing threads.
//     - Only thread-safe functions may be called in this mode.
//     - Can be acquired in parallel with read mode.
//     - Blocks until no thread holds the mutex in unique or read-only mode.
//     - Stops other threads acquiring in unique and read-only mode until released.
// The mutex is ordered meaning it prioritises older acquires over newer ones.
// It also supports cancelling waiting through a CancelManager instance.
// The mutex is compatible with std::shared_timed_mutex and the std::*_lock classes
class OrderedMutex {
protected:
    enum class LockState {
        Unlocked,
        Unique,
        Shared,
        SharedReadOnly,
        SharedRead,
        SharedReadWrite
    };
    struct ThreadState {
        std::thread::id id;
        LockState state;
        LockState desired_state;
    };

    std::mutex mutex;
    std::condition_variable condition;
    // The state the mutex is currently in.
    LockState state = LockState::Unlocked;
    // The number of threads locked in read-only mode.
    size_t read_only_count = 0;
    // The number of threads locked in read-write mode.
    size_t read_write_count = 0;
    // The threads that currently hold the lock.
    std::list<ThreadState> locked_threads;
    // The pending threads in the order the lock call was made.
    std::list<ThreadState> pending_threads;
    // Lookup from thread id to the iterator in locked_threads or pending_thread.
    std::map<std::thread::id, std::list<ThreadState>::iterator> threads;

    template <bool ReturnBool, bool Blocking, LockState DesiredState, class... Args>
        requires(DesiredState != LockState::Unlocked && DesiredState != LockState::Shared)
    std::conditional_t<ReturnBool, bool, void> _lock_imp(Args... args_pack)
    {
        // Lock the state.
        std::unique_lock lock(mutex);

        // Get the thread id
        auto id = std::this_thread::get_id();

        // Check for a deadlock.
        if (threads.find(id) != threads.end()) {
            throw Deadlock("Deadlock encountered.");
        }

        // Is mutex in a lockable state.
        auto is_needed_state = [&]() -> bool {
            if constexpr (DesiredState == LockState::SharedReadOnly) {
                return state == LockState::Unlocked || (state == LockState::Shared && read_write_count == 0);
            } else if constexpr (DesiredState == LockState::SharedRead) {
                return state != LockState::Unique;
            } else if constexpr (DesiredState == LockState::SharedReadWrite) {
                return state == LockState::Unlocked || (state == LockState::Shared && read_only_count == 0);
            } else {
                static_assert(DesiredState == LockState::Unique);
                return state == LockState::Unlocked;
            }
        };

        auto set_state = [&]() {
            if constexpr (DesiredState == LockState::SharedReadOnly) {
                state = LockState::Shared;
                read_only_count++;
            } else if constexpr (DesiredState == LockState::SharedRead) {
                state = LockState::Shared;
            } else if constexpr (DesiredState == LockState::SharedReadWrite) {
                state = LockState::Shared;
                read_write_count++;
            } else {
                static_assert(DesiredState == LockState::Unique);
                state = LockState::Unique;
            }
        };

        if (pending_threads.empty() && is_needed_state()) {
            // mutex can be locked without blocking. Lock it.
            set_state();
            auto it = locked_threads.insert(locked_threads.end(), { id, DesiredState, DesiredState });
            threads.emplace(id, it);
            if constexpr (ReturnBool) {
                return true;
            }
        } else if constexpr (Blocking) {
            // Wait until the mutex can be locked.

            // Unpack the args
            auto args = std::tie(args_pack...);
            AbstractCancelManager& cancel_manager = std::get<std::tuple_size_v<decltype(args)> - 1>(args);

            // Create the lock state
            auto it = pending_threads.insert(pending_threads.end(), { id, LockState::Unlocked, DesiredState });
            threads.emplace(id, it);

            auto is_lockable = [&]() -> bool {
                return pending_threads.begin() == it && is_needed_state();
            };

            // If the state does not get locked it must be erased.
            auto erase_state = [&]() -> void {
                threads.erase(it->id);
                pending_threads.erase(it);

                // Notify other threads if the top pending thread changes.
                if (it == pending_threads.begin()) {
                    condition.notify_all();
                }
            };

            // Function to lock the mutex.
            auto lock_state = [&]() -> void {
                // Update the mutex state
                set_state();

                // Move the thread state
                locked_threads.splice(locked_threads.end(), pending_threads, pending_threads.begin());
                it->state = DesiredState;

                // Notify other threads that the top pending thread changed.
                condition.notify_all();
            };

            auto on_cancel = [&]() -> void {
                condition.notify_all();
            };
            cancel_manager.register_cancel_callback(on_cancel);

            auto unregister_cancel = [&]() -> void {
                cancel_manager.unregister_cancel_callback(on_cancel);
            };

            if constexpr (ReturnBool) {
                static_assert(std::tuple_size_v<decltype(args)> == 2);
                const auto& timeout = std::get<0>(args);
                using TimeoutT = std::remove_cvref_t<decltype(timeout)>;

                auto wait = [&](std::unique_lock<std::mutex>& _lck, decltype(timeout) _timeout, std::function<bool()> _pred) -> bool {
                    if constexpr (is_specialization_of<std::chrono::duration, TimeoutT>::value) {
                        return condition.wait_for(_lck, _timeout, _pred);
                    } else {
                        static_assert(is_specialization_of<std::chrono::time_point, TimeoutT>::value);
                        return condition.wait_until(_lck, _timeout, _pred);
                    }
                };

                auto result = wait(lock, timeout, [&] { return cancel_manager.is_cancel_requested() || is_lockable(); });
                unregister_cancel();
                if (result && !cancel_manager.is_cancel_requested()) {
                    lock_state();
                    return true;
                } else {
                    erase_state();
                    return false;
                }
            } else {
                // Wait until this is at the top of the queue and the mutex is unlocked.
                condition.wait(lock, [&] {
                if (cancel_manager.is_cancel_requested()) {
                    erase_state();
                    unregister_cancel();
                    throw TaskCancelled();
                }
                return is_lockable(); });

                unregister_cancel();
                lock_state();
            }
        } else if constexpr (ReturnBool) {
            return false;
        }
    }

    template <bool ReturnBool, bool Blocking, LockState DesiredState, class... TimeoutTs>
    std::conditional_t<ReturnBool, bool, void> _lock(TimeoutTs... timeout, AbstractCancelManager& cancel_manager)
    {
        return _lock_imp<ReturnBool, Blocking, DesiredState, TimeoutTs..., AbstractCancelManager&>(timeout..., cancel_manager);
    }

    template <bool ReturnBool, bool Blocking, LockState DesiredState>
    std::conditional_t<ReturnBool, bool, void> _lock()
    {
        return _lock_imp<ReturnBool, Blocking, DesiredState>();
    }

    template <LockState required_state>
        requires(required_state == LockState::Shared || required_state == LockState::Unique)
    void _unlock()
    {
        // Lock the state.
        std::unique_lock lock(mutex);

        // Get the thread id
        auto id = std::this_thread::get_id();

        // Find the thread state
        auto it = threads.find(id);

        // Ensure that the mutex is locked in the same mode by the thread.
        if (it == threads.end()) {
            throw std::runtime_error("This mutex is not locked by this thread.");
        }
        if constexpr (required_state == LockState::Unique) {
            if (it->second->state != LockState::Unique) {
                throw std::runtime_error("This mutex is not locked in unique mode by this thread.");
            }
        } else {
            static_assert(required_state == LockState::Shared);
            switch (it->second->state) {
            case LockState::SharedReadOnly:
                read_only_count--;
            case LockState::SharedRead:
                break;
            case LockState::SharedReadWrite:
                read_write_count--;
            default:
                throw std::runtime_error("This mutex is not locked in shared mode by this thread.");
            }
        }

        // Remove the thread state
        locked_threads.erase(it->second);
        threads.erase(it);

        // Reset mutex state
        if constexpr (required_state == LockState::Unique) {
            state = LockState::Unlocked;
        } else {
            static_assert(required_state == LockState::Shared);
            if (locked_threads.empty()) {
                state = LockState::Unlocked;
                if (read_only_count != 0 || read_write_count != 0) {
                    throw std::runtime_error("Shared thread counts are not zero.");
                }
            }
        }

        // Wake up pending threads
        condition.notify_all();
    }

public:
    // Constructors
    AMULET_CORE_EXPORT OrderedMutex();
    OrderedMutex(const OrderedMutex&) = delete;
    OrderedMutex(OrderedMutex&&) = delete;

    // Destructor
    AMULET_CORE_EXPORT ~OrderedMutex();

    // Locks the mutex in unique mode.
    // Blocks until no thread holds the mutex.
    // Stops all other threads acquiring the mutex until released.
    // A cancel manager can be defined to support aborting the wait. TaskCancelled is thrown if task is cancelled.
    // Thread safe.
    AMULET_CORE_EXPORT void lock(AbstractCancelManager& cancel_manager = global_VoidCancelManager);

    // Tries to lock the mutex in unique mode, non-blocking.
    // Returns true if the mutex was locked, false if it wasn't.
    // Thread safe
    AMULET_CORE_EXPORT bool try_lock();

    // Like try_lock but with a timeout duration.
    // Returns true if the mutex was locked, false if it wasn't.
    // A cancel manager can be defined to support aborting the wait. TaskCancelled is thrown if task is cancelled.
    // Thread safe.
    template <class Rep, class Period>
    bool try_lock_for(const std::chrono::duration<Rep, Period>& timeout_duration, AbstractCancelManager& cancel_manager = global_VoidCancelManager)
    {
        return _lock<true, true, LockState::Unique, const std::chrono::duration<Rep, Period>&>(timeout_duration, cancel_manager);
    }

    // Like try_lock but with a timeout time.
    // Returns true if the mutex was locked, false if it wasn't.
    // A cancel manager can be defined to support aborting the wait. TaskCancelled is thrown if task is cancelled.
    // Thread safe.
    template <class Clock, class Duration>
    bool try_lock_until(const std::chrono::time_point<Clock, Duration>& timeout_time, AbstractCancelManager& cancel_manager = global_VoidCancelManager)
    {
        return _lock<true, true, LockState::Unique, const std::chrono::time_point<Clock, Duration>&>(timeout_time, cancel_manager);
    }

    // Unlock the mutex from unique mode.
    // Must be called by the thread that locked it.
    // Thread safe.
    AMULET_CORE_EXPORT void unlock();

    // Locks the mutex in shared read-only mode.
    // Blocks until no thread holds the mutex in unique or write mode.
    // Stops other threads acquiring in unique and write mode until released.
    // A cancel manager can be defined to support aborting the wait. TaskCancelled is thrown if task is cancelled.
    // Thread safe.
    AMULET_CORE_EXPORT void lock_shared_read_only(AbstractCancelManager& cancel_manager = global_VoidCancelManager);

    // Tries to lock the mutex in shared read-only mode, non-blocking.
    // Returns true if the mutex was locked, false if it wasn't.
    // Thread safe
    AMULET_CORE_EXPORT bool try_lock_shared_read_only();

    // Like lock_shared_read_only but with a timeout duration.
    // Returns true if the mutex was locked, false if it wasn't.
    // A cancel manager can be defined to support aborting the wait. TaskCancelled is thrown if task is cancelled.
    // Thread safe.
    template <class Rep, class Period>
    bool try_lock_shared_read_only_for(const std::chrono::duration<Rep, Period>& timeout_duration, AbstractCancelManager& cancel_manager = global_VoidCancelManager)
    {
        return _lock<true, true, LockState::SharedReadOnly, const std::chrono::duration<Rep, Period>&>(timeout_duration, cancel_manager);
    }

    // Like lock_shared_read_only but with a timeout time.
    // Returns true if the mutex was locked, false if it wasn't.
    // A cancel manager can be defined to support aborting the wait. TaskCancelled is thrown if task is cancelled.
    // Thread safe.
    template <class Clock, class Duration>
    bool try_lock_shared_read_only_until(const std::chrono::time_point<Clock, Duration>& timeout_time, AbstractCancelManager& cancel_manager = global_VoidCancelManager)
    {
        return _lock<true, true, LockState::SharedReadOnly, const std::chrono::time_point<Clock, Duration>&>(timeout_time, cancel_manager);
    }

    // Locks the mutex in shared read mode.
    // Blocks until no thread holds the mutex in unique mode.
    // Stops other threads acquiring in unique mode until released.
    // A cancel manager can be defined to support aborting the wait. TaskCancelled is thrown if task is cancelled.
    // Thread safe.
    AMULET_CORE_EXPORT void lock_shared_read(AbstractCancelManager& cancel_manager = global_VoidCancelManager);

    // Tries to lock the mutex in shared read mode, non-blocking.
    // Returns true if the mutex was locked, false if it wasn't.
    // Thread safe
    AMULET_CORE_EXPORT bool try_lock_shared_read();

    // Like lock_shared_read but with a timeout duration.
    // Returns true if the mutex was locked, false if it wasn't.
    // A cancel manager can be defined to support aborting the wait. TaskCancelled is thrown if task is cancelled.
    // Thread safe.
    template <class Rep, class Period>
    bool try_lock_shared_read_for(const std::chrono::duration<Rep, Period>& timeout_duration, AbstractCancelManager& cancel_manager = global_VoidCancelManager)
    {
        return _lock<true, true, LockState::SharedRead, const std::chrono::duration<Rep, Period>&>(timeout_duration, cancel_manager);
    }

    // Like lock_shared_read but with a timeout time.
    // Returns true if the mutex was locked, false if it wasn't.
    // A cancel manager can be defined to support aborting the wait. TaskCancelled is thrown if task is cancelled.
    // Thread safe.
    template <class Clock, class Duration>
    bool try_lock_shared_read_until(const std::chrono::time_point<Clock, Duration>& timeout_time, AbstractCancelManager& cancel_manager = global_VoidCancelManager)
    {
        return _lock<true, true, LockState::SharedRead, const std::chrono::time_point<Clock, Duration>&>(timeout_time, cancel_manager);
    }

    // Locks the mutex in shared read-write mode.
    // Blocks until no thread holds the mutex in unique or read-only mode.
    // Stops other threads acquiring in unique and read-only mode until released.
    // A cancel manager can be defined to support aborting the wait. TaskCancelled is thrown if task is cancelled.
    // Thread safe.
    AMULET_CORE_EXPORT void lock_shared_read_write(AbstractCancelManager& cancel_manager = global_VoidCancelManager);

    // Tries to lock the mutex in shared read-write mode, non-blocking.
    // Returns true if the mutex was locked, false if it wasn't.
    // Thread safe
    AMULET_CORE_EXPORT bool try_lock_shared_read_write();

    // Like lock_shared_read_write but with a timeout duration.
    // Returns true if the mutex was locked, false if it wasn't.
    // A cancel manager can be defined to support aborting the wait. TaskCancelled is thrown if task is cancelled.
    // Thread safe.
    template <class Rep, class Period>
    bool try_lock_shared_read_write_for(const std::chrono::duration<Rep, Period>& timeout_duration, AbstractCancelManager& cancel_manager = global_VoidCancelManager)
    {
        return _lock<true, true, LockState::SharedReadWrite, const std::chrono::duration<Rep, Period>&>(timeout_duration, cancel_manager);
    }

    // Like lock_shared_read_write but with a timeout time.
    // Returns true if the mutex was locked, false if it wasn't.
    // A cancel manager can be defined to support aborting the wait. TaskCancelled is thrown if task is cancelled.
    // Thread safe.
    template <class Clock, class Duration>
    bool try_lock_shared_read_write_until(const std::chrono::time_point<Clock, Duration>& timeout_time, AbstractCancelManager& cancel_manager = global_VoidCancelManager)
    {
        return _lock<true, true, LockState::SharedReadWrite, const std::chrono::time_point<Clock, Duration>&>(timeout_time, cancel_manager);
    }

    // Alias of lock_shared_read_only
    AMULET_CORE_EXPORT void lock_shared(AbstractCancelManager& cancel_manager = global_VoidCancelManager);

    // Alias of try_lock_shared_read_only
    AMULET_CORE_EXPORT bool try_lock_shared();

    // Alias of try_lock_shared_read_only_for
    template <class Rep, class Period>
    bool try_lock_shared_for(const std::chrono::duration<Rep, Period>& timeout_duration, AbstractCancelManager& cancel_manager = global_VoidCancelManager)
    {
        return try_lock_shared_read_only_for<Rep, Period>(timeout_duration, cancel_manager);
    }

    // Alias of try_lock_shared_read_only_until
    template <class Clock, class Duration>
    bool try_lock_shared_until(const std::chrono::time_point<Clock, Duration>& timeout_time, AbstractCancelManager& cancel_manager = global_VoidCancelManager)
    {
        return try_lock_shared_read_only_until<Clock, Duration>(timeout_time, cancel_manager);
    }

    // Unlock the mutex from any shared mode.
    // Must be called by the thread that locked it.
    // Thread safe.
    AMULET_CORE_EXPORT void unlock_shared();
};
} // namespace Amulet
