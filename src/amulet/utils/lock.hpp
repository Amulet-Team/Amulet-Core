#include <chrono>
#include <condition_variable>
#include <list>
#include <map>
#include <mutex>
#include <stdexcept>

#include <amulet/dll.hpp>

namespace Amulet {

class Deadlock : public std::runtime_error {
public:
    std::runtime_error::runtime_error;
};

// std::shared_timed_mutex does not have order priority meaning that an older lock call can be blocked by newer lock_shared calls.
// This is a variant of std::shared_timed_mutex that prioritises call order.
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
    std::map<std::thread::id, std::list<ThreadState>::iterator&> threads;

public:
    // Constructors
    OrderedSharedMutex() = default;
    OrderedSharedMutex(const OrderedSharedMutex&) = delete;

    // Unique
    AMULET_CORE_DLLX void lock();
    AMULET_CORE_DLLX bool try_lock();
    AMULET_CORE_DLLX void unlock();

    // Shared
    AMULET_CORE_DLLX void lock_shared();
    AMULET_CORE_DLLX bool try_lock_shared();
    AMULET_CORE_DLLX void unlock_shared();
};

class OrderedSharedTimedMutex : public OrderedSharedMutex {
public:
    // Constructors
    OrderedSharedTimedMutex() = default;
    OrderedSharedTimedMutex(const OrderedSharedTimedMutex&) = delete;

    // Unique
    template <class Rep, class Period>
    bool try_lock_for(const std::chrono::duration<Rep, Period>& timeout_duration) { 
        // Lock the state.
        std::unique_lock lock(mutex);

        // Get the thread id
        auto id = std::this_thread::get_id();

        // Check for a deadlock.
        if (threads.find(id) != threads.end()) {
            throw Deadlock("Deadlock encountered.");
        }

        if (pending_threads.empty() && state == LockState::Unlocked) {
            // mutex is not locked and there are no pending threads. Lock it.
            state = LockState::Unique;
            auto it = locked_threads.insert(locked_threads.end(), { id, LockState::Unique, LockState::Unique });
            threads.emplace(id, it);
            return true;
        } else {
            // mutex is locked or there are pending threads. Wait.

            // Create the lock state
            auto it = pending_threads.insert(pending_threads.end(), { id, LockState::Unlocked, LockState::Unique });
            threads.emplace(id, it);

            // Wait until this is at the top of the queue and the mutex is unlocked.
            if (condition.wait_for(lock, timeout_duration, [&] { return pending_threads.begin() == it && state == LockState::Unlocked; })) {
                // Update the mutex state
                state = LockState::Unique;

                // Move the thread state
                locked_threads.splice(locked_threads.end(), pending_threads, pending_threads.begin());
                it->state = LockState::Unique;
                return true;
            } else {
                return false;
            }
        }
    }
    template <class Clock, class Duration>
    bool try_lock_until(const std::chrono::time_point<Clock, Duration>& timeout_time) {
        // Lock the state.
        std::unique_lock lock(mutex);

        // Get the thread id
        auto id = std::this_thread::get_id();

        // Check for a deadlock.
        if (threads.find(id) != threads.end()) {
            throw Deadlock("Deadlock encountered.");
        }

        if (pending_threads.empty() && state == LockState::Unlocked) {
            // mutex is not locked and there are no pending threads. Lock it.
            state = LockState::Unique;
            auto it = locked_threads.insert(locked_threads.end(), { id, LockState::Unique, LockState::Unique });
            threads.emplace(id, it);
            return true;
        } else {
            // mutex is locked or there are pending threads. Wait.

            // Create the lock state
            auto it = pending_threads.insert(pending_threads.end(), { id, LockState::Unlocked, LockState::Unique });
            threads.emplace(id, it);

            // Wait until this is at the top of the queue and the mutex is unlocked.
            if (condition.wait_until(lock, timeout_time, [&] { return pending_threads.begin() == it && state == LockState::Unlocked; })) {
                // Update the mutex state
                state = LockState::Unique;

                // Move the thread state
                locked_threads.splice(locked_threads.end(), pending_threads, pending_threads.begin());
                it->state = LockState::Unique;
                return true;
            } else {
                return false;
            }
        }
    }

    // Shared
    template <class Rep, class Period>
    bool try_lock_shared_for(const std::chrono::duration<Rep, Period>& timeout_duration) {
        // Lock the state.
        std::unique_lock lock(mutex);

        // Get the thread id
        auto id = std::this_thread::get_id();

        // Check for a deadlock.
        if (threads.find(id) != threads.end()) {
            throw Deadlock("Deadlock encountered.");
        }

        if (pending_threads.empty() && state != LockState::Unique) {
            // mutex is not locked and there are no pending threads. Lock it.
            state = LockState::Shared;
            auto it = locked_threads.insert(locked_threads.end(), { id, LockState::Shared, LockState::Shared });
            threads.emplace(id, it);
            return true;
        } else {
            // mutex is locked or there are pending threads. Wait.

            // Create the lock state
            auto it = pending_threads.insert(pending_threads.end(), { id, LockState::Unlocked, LockState::Shared });
            threads.emplace(id, it);

            // Wait until this is at the top of the queue and the mutex is unlocked.
            if (condition.wait_for(lock, timeout_duration, [&] { return pending_threads.begin() == it && state != LockState::Unique; })) {
                // Update the mutex state
                state = LockState::Shared;

                // Move the thread state
                locked_threads.splice(locked_threads.end(), pending_threads, pending_threads.begin());
                it->state = LockState::Shared;
                return true;
            } else {
                return false;
            }
        }
    }
    template <class Clock, class Duration>
    bool try_lock_shared_until(const std::chrono::time_point<Clock, Duration>& timeout_time) {
        // Lock the state.
        std::unique_lock lock(mutex);

        // Get the thread id
        auto id = std::this_thread::get_id();

        // Check for a deadlock.
        if (threads.find(id) != threads.end()) {
            throw Deadlock("Deadlock encountered.");
        }

        if (pending_threads.empty() && state != LockState::Unique) {
            // mutex is not locked and there are no pending threads. Lock it.
            state = LockState::Shared;
            auto it = locked_threads.insert(locked_threads.end(), { id, LockState::Shared, LockState::Shared });
            threads.emplace(id, it);
            return true;
        } else {
            // mutex is locked or there are pending threads. Wait.

            // Create the lock state
            auto it = pending_threads.insert(pending_threads.end(), { id, LockState::Unlocked, LockState::Shared });
            threads.emplace(id, it);

            // Wait until this is at the top of the queue and the mutex is unlocked.
            if (condition.wait_until(lock, timeout_time, [&] { return pending_threads.begin() == it && state != LockState::Unique; })) {
                // Update the mutex state
                state = LockState::Shared;

                // Move the thread state
                locked_threads.splice(locked_threads.end(), pending_threads, pending_threads.begin());
                it->state = LockState::Shared;
                return true;
            } else {
                return false;
            }
        }
    }
};
} // namespace Amulet
