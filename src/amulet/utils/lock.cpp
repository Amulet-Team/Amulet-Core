#include "lock.hpp"

namespace Amulet {

AMULET_CORE_DLLX void OrderedSharedMutex::lock()
{
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
    } else {
        // mutex is locked or there are pending threads. Wait.

        // Create the lock state
        auto it = pending_threads.insert(pending_threads.end(), { id, LockState::Unlocked, LockState::Unique });
        threads.emplace(id, it);

        // Wait until this is at the top of the queue and the mutex is unlocked.
        condition.wait(lock, [&] { return pending_threads.begin() == it && state == LockState::Unlocked; });

        // Update the mutex state
        state = LockState::Unique;

        // Move the thread state
        locked_threads.splice(locked_threads.end(), pending_threads, pending_threads.begin());
        it->state = LockState::Unique;
    }
}
AMULET_CORE_DLLX bool OrderedSharedMutex::try_lock()
{
    // Lock the state.
    std::unique_lock lock(mutex);

    // Get the thread id
    auto id = std::this_thread::get_id();

    // Check for a deadlock.
    if (threads.find(id) != threads.end()) {
        throw Deadlock("Deadlock encountered.");
    }

    if (pending_threads.empty() && state == LockState::Unlocked) {
        // mutex is lockable. Lock it.
        state = LockState::Unique;
        auto it = locked_threads.insert(locked_threads.end(), { id, LockState::Unique, LockState::Unique });
        threads.emplace(id, it);
        return true;
    } else {
        // mutex is not lockable.
        return false;
    }
}
AMULET_CORE_DLLX void OrderedSharedMutex::unlock()
{
    // Lock the state.
    std::unique_lock lock(mutex);

    // Get the thread id
    auto id = std::this_thread::get_id();

    // Find the thread state
    auto it = threads.find(id);

    // Ensure that the mutex is locked in unique mode by the thread.
    if (it == threads.end() || it->second->state != LockState::Unique) {
        throw std::runtime_error("This mutex is not locked in unique mode by this thread.");
    }

    locked_threads.erase(it->second);
    threads.erase(it);
}

AMULET_CORE_DLLX void OrderedSharedMutex::lock_shared()
{
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
    } else {
        // mutex is locked or there are pending threads. Wait.

        // Create the lock state
        auto it = pending_threads.insert(pending_threads.end(), { id, LockState::Unlocked, LockState::Shared });
        threads.emplace(id, it);

        // Wait until this is at the top of the queue and the mutex is unlocked.
        condition.wait(lock, [&] { return pending_threads.begin() == it && state != LockState::Unique; });

        // Update the mutex state
        state = LockState::Shared;

        // Move the thread state
        locked_threads.splice(locked_threads.end(), pending_threads, pending_threads.begin());
        it->state = LockState::Shared;
    }
}
AMULET_CORE_DLLX bool OrderedSharedMutex::try_lock_shared()
{
    // Lock the state.
    std::unique_lock lock(mutex);

    // Get the thread id
    auto id = std::this_thread::get_id();

    // Check for a deadlock.
    if (threads.find(id) != threads.end()) {
        throw Deadlock("Deadlock encountered.");
    }

    if (pending_threads.empty() && state != LockState::Unique) {
        // mutex is lockable. Lock it.
        state = LockState::Shared;
        auto it = locked_threads.insert(locked_threads.end(), { id, LockState::Shared, LockState::Shared });
        threads.emplace(id, it);
        return true;
    } else {
        // mutex is not lockable.
        return false;
    }
}
AMULET_CORE_DLLX void OrderedSharedMutex::unlock_shared()
{
    // Lock the state.
    std::unique_lock lock(mutex);

    // Get the thread id
    auto id = std::this_thread::get_id();

    // Find the thread state
    auto it = threads.find(id);

    // Ensure that the mutex is locked in unique mode by the thread.
    if (it == threads.end() || it->second->state != LockState::Shared) {
        throw std::runtime_error("This mutex is not locked in shared mode by this thread.");
    }

    locked_threads.erase(it->second);
    threads.erase(it);
}

} // namespace Amulet
