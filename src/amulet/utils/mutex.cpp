#include "mutex.hpp"

namespace Amulet {

// OrderedMutex
OrderedMutex::OrderedMutex() = default;
OrderedMutex::~OrderedMutex() = default;
void OrderedMutex::lock(AbstractCancelManager& cancel_manager)
{
    _lock<false, true, LockState::Unique>(cancel_manager);
}
bool OrderedMutex::try_lock()
{
    return _lock<true, false, LockState::Unique>();
}
void OrderedMutex::unlock()
{
    _unlock<LockState::Unique>();
}

void OrderedMutex::lock_shared_read_only(AbstractCancelManager& cancel_manager)
{
    _lock<false, true, LockState::SharedReadOnly>(cancel_manager);
}
bool OrderedMutex::try_lock_shared_read_only()
{
    return _lock<true, false, LockState::SharedReadOnly>();
}

void OrderedMutex::lock_shared_read(AbstractCancelManager& cancel_manager)
{
    _lock<false, true, LockState::SharedRead>(cancel_manager);
}
bool OrderedMutex::try_lock_shared_read()
{
    return _lock<true, false, LockState::SharedRead>();
}

void OrderedMutex::lock_shared_read_write(AbstractCancelManager& cancel_manager)
{
    _lock<false, true, LockState::SharedReadWrite>(cancel_manager);
}
bool OrderedMutex::try_lock_shared_read_write()
{
    return _lock<true, false, LockState::SharedReadWrite>();
}

void OrderedMutex::lock_shared(AbstractCancelManager& cancel_manager)
{
    lock_shared_read_only(cancel_manager);
}
bool OrderedMutex::try_lock_shared()
{
    return try_lock_shared_read_only();
}
void OrderedMutex::unlock_shared()
{
    _unlock<LockState::Shared>();
}

} // namespace Amulet
