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

class Deadlock : public std::runtime_error {
public:
    AMULET_CORE_DLLX explicit Deadlock(const std::string& msg);
    AMULET_CORE_DLLX Deadlock();
    AMULET_CORE_DLLX ~Deadlock() noexcept override;
    AMULET_CORE_DLLX const char* what() const override;
};

// std::shared_timed_mutex does not have order priority meaning that an older lock call can be blocked by newer lock_shared calls.
// This is a variant of std::shared_timed_mutex that prioritises call order.
// It also supports cancelling waiting through a CancelManager instance.
class OrderedSharedMutex {
protected:
    enum class LockState {
        Unlocked,
        Shared,
        Unique
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
    // The threads that currently hold the lock.
    std::list<ThreadState> locked_threads;
    // The pending threads in the order the lock call was made.
    std::list<ThreadState> pending_threads;
    // Lookup from thread id to the iterator in locked_threads or pending_thread.
    std::map<std::thread::id, std::list<ThreadState>::iterator> threads;

    template <bool ReturnBool, bool Blocking, LockState DesiredState, class... Args>
        requires(DesiredState == LockState::Shared || DesiredState == LockState::Unique)
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
            if constexpr (DesiredState == LockState::Shared) {
                return state != LockState::Unique;
            } else {
                static_assert(DesiredState == LockState::Unique);
                return state == LockState::Unlocked;
            }
        };

        if (pending_threads.empty() && is_needed_state()) {
            // mutex can be locked without blocking. Lock it.
            state = DesiredState;
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
                state = DesiredState;

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

        // Ensure that the mutex is locked in unique mode by the thread.
        if (it == threads.end() || it->second->state != required_state) {
            if constexpr (required_state == LockState::Unique) {
                throw std::runtime_error("This mutex is not locked in unique mode by this thread.");
            } else {
                static_assert(required_state == LockState::Shared);
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
            }
        }

        // Wake up pending threads
        condition.notify_all();
    }

public:
    // Constructors
    AMULET_CORE_DLLX OrderedSharedMutex();
    OrderedSharedMutex(const OrderedSharedMutex&) = delete;
    OrderedSharedMutex(OrderedSharedMutex&&) = delete;

    // Destructor
    AMULET_CORE_DLLX ~OrderedSharedMutex();

    // Unique
    AMULET_CORE_DLLX void lock(AbstractCancelManager& cancel_manager = global_VoidCancelManager);
    AMULET_CORE_DLLX bool try_lock();
    AMULET_CORE_DLLX void unlock();

    // Shared
    AMULET_CORE_DLLX void lock_shared(AbstractCancelManager& cancel_manager = global_VoidCancelManager);
    AMULET_CORE_DLLX bool try_lock_shared();
    AMULET_CORE_DLLX void unlock_shared();
};

class OrderedSharedTimedMutex : public OrderedSharedMutex {
public:
    // Constructors
    AMULET_CORE_DLLX OrderedSharedTimedMutex();
    OrderedSharedTimedMutex(const OrderedSharedTimedMutex&) = delete;
    OrderedSharedTimedMutex(OrderedSharedTimedMutex&&) = delete;

    // Destructor
    AMULET_CORE_DLLX ~OrderedSharedTimedMutex();

    // Unique
    template <class Rep, class Period>
    bool try_lock_for(const std::chrono::duration<Rep, Period>& timeout_duration, AbstractCancelManager& cancel_manager = global_VoidCancelManager)
    {
        return _lock<true, true, LockState::Unique, const std::chrono::duration<Rep, Period>&>(timeout_duration, cancel_manager);
    }
    template <class Clock, class Duration>
    bool try_lock_until(const std::chrono::time_point<Clock, Duration>& timeout_time, AbstractCancelManager& cancel_manager = global_VoidCancelManager)
    {
        return _lock<true, true, LockState::Unique, const std::chrono::time_point<Clock, Duration>&>(timeout_time, cancel_manager);
    }

    // Shared
    template <class Rep, class Period>
    bool try_lock_shared_for(const std::chrono::duration<Rep, Period>& timeout_duration, AbstractCancelManager& cancel_manager = global_VoidCancelManager)
    {
        return _lock<true, true, LockState::Shared, const std::chrono::duration<Rep, Period>&>(timeout_duration, cancel_manager);
    }
    template <class Clock, class Duration>
    bool try_lock_shared_until(const std::chrono::time_point<Clock, Duration>& timeout_time, AbstractCancelManager& cancel_manager = global_VoidCancelManager)
    {
        return _lock<true, true, LockState::Shared, const std::chrono::time_point<Clock, Duration>&>(timeout_time, cancel_manager);
    }
};
} // namespace Amulet
