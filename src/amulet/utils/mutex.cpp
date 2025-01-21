#include "mutex.hpp"

namespace Amulet {

Deadlock::Deadlock(const std::string& msg)
    : std::runtime_error(msg)
{
}
Deadlock::Deadlock()
    : Deadlock("Deadlock")
{
}
Deadlock::~Deadlock() = default;
const char* Deadlock::what() const noexcept { return std::runtime_error::what(); }

AMULET_CORE_DLLX void OrderedSharedMutex::lock(AbstractCancelManager& cancel_manager)
{
    _lock<false, true, LockState::Unique>(cancel_manager);
}
AMULET_CORE_DLLX bool OrderedSharedMutex::try_lock()
{
    return _lock<true, false, LockState::Unique>();
}
AMULET_CORE_DLLX void OrderedSharedMutex::unlock()
{
    _unlock<LockState::Unique>();
}

AMULET_CORE_DLLX void OrderedSharedMutex::lock_shared(AbstractCancelManager& cancel_manager)
{
    _lock<false, true, LockState::Shared>(cancel_manager);
}
AMULET_CORE_DLLX bool OrderedSharedMutex::try_lock_shared()
{
    return _lock<true, false, LockState::Shared>();
}
AMULET_CORE_DLLX void OrderedSharedMutex::unlock_shared()
{
    _unlock<LockState::Shared>();
}

} // namespace Amulet
