#include "mutex.hpp"

namespace Amulet {

// OrderedMutex
OrderedMutex::OrderedMutex() = default;
OrderedMutex::~OrderedMutex() = default;

void OrderedMutex::unlock()
{
    // Lock the state.
    std::unique_lock lock(mutex);

    // Get the thread id
    auto id = std::this_thread::get_id();

    // Find the thread state
    auto it = threads.find(id);

    // Ensure that the mutex is locked in the same mode by the thread.
    if (it == threads.end() || !it->second->state.has_value()) {
        throw std::runtime_error("This mutex is not locked by this thread.");
    }

    switch (it->second->state->first) {
    case ThreadAccessMode::Read:
        read_count--;
        break;
    case ThreadAccessMode::ReadWrite:
        read_count--;
        write_count--;
        break;
    }

    switch (it->second->state->second) {
    case ThreadShareMode::Unique:
        blocking_read_count--;
        blocking_write_count--;
        break;
    case ThreadShareMode::SharedReadOnly:
        blocking_write_count--;
        break;
    }

    // Remove the thread state
    locked_threads.erase(it->second);
    threads.erase(it);

    // Wake up pending threads
    condition.notify_all();
}

} // namespace Amulet
