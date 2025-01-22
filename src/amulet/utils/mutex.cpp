#include "mutex.hpp"

namespace Amulet {

// Deadlock
Deadlock::Deadlock(const std::string& msg)
    : std::runtime_error(msg)
{
}
Deadlock::Deadlock()
    : Deadlock("Deadlock")
{
}
Deadlock::~Deadlock() noexcept = default;
const char* Deadlock::what() const noexcept { return std::runtime_error::what(); }

// OrderedSharedMutex
OrderedSharedMutex::OrderedSharedMutex() = default;
OrderedSharedMutex::~OrderedSharedMutex() = default;
void OrderedSharedMutex::lock(AbstractCancelManager& cancel_manager)
{
    _lock<false, true, LockState::Unique>(cancel_manager);
}
bool OrderedSharedMutex::try_lock()
{
    return _lock<true, false, LockState::Unique>();
}
void OrderedSharedMutex::unlock()
{
    _unlock<LockState::Unique>();
}

void OrderedSharedMutex::lock_shared(AbstractCancelManager& cancel_manager)
{
    _lock<false, true, LockState::Shared>(cancel_manager);
}
bool OrderedSharedMutex::try_lock_shared()
{
    return _lock<true, false, LockState::Shared>();
}
void OrderedSharedMutex::unlock_shared()
{
    _unlock<LockState::Shared>();
}

// OrderedSharedTimedMutex
OrderedSharedTimedMutex::OrderedSharedTimedMutex() = default;
OrderedSharedTimedMutex::~OrderedSharedTimedMutex() = default;

} // namespace Amulet
