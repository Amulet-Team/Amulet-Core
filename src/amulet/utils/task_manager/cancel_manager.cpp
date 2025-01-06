#include <functional>
#include <list>
#include <mutex>
#include <stdexcept>

#include "cancel_manager.hpp"

namespace Amulet {

AMULET_CORE_DLLX TaskCancelled::TaskCancelled(std::string msg)
    : msg(msg)
{
}
AMULET_CORE_DLLX TaskCancelled::TaskCancelled()
    : TaskCancelled("Task Cancelled")
{
}
const char* TaskCancelled::what() const noexcept { return msg.c_str(); }

AMULET_CORE_DLLX VoidCancelManager::VoidCancelManager() {};
void VoidCancelManager::cancel() { }
bool VoidCancelManager::is_cancel_requested() { return false; }
void VoidCancelManager::register_cancel_callback(CancelCallback callback) {};
void VoidCancelManager::unregister_cancel_callback(CancelCallback callback) {};

detail::InternalCancelManager::InternalCancelManager(
    std::mutex& cancel_mutex,
    bool& cancelled,
    std::list<CancelCallback>& cancel_callbacks)
    : _cancelled(cancelled)
    , _cancel_mutex(cancel_mutex)
    , _cancel_callbacks(cancel_callbacks)
{
}
void detail::InternalCancelManager::cancel()
{
    std::lock_guard<std::mutex> guard(_cancel_mutex);
    if (_cancelled) {
        return;
    }
    _cancelled = true;
    for (const auto& callback : _cancel_callbacks) {
        callback();
    }
}
bool detail::InternalCancelManager::is_cancel_requested()
{
    return _cancelled;
}
void detail::InternalCancelManager::register_cancel_callback(CancelCallback callback)
{
    std::lock_guard<std::mutex> guard(_cancel_mutex);
    // Add the callback to the end.
    _cancel_callbacks.push_back(callback);
}
void detail::InternalCancelManager::unregister_cancel_callback(CancelCallback callback)
{
    std::lock_guard<std::mutex> guard(_cancel_mutex);
    // Remove all callbacks matching the given callback.
    _cancel_callbacks.remove_if(
        [&callback](CancelCallback callback_) { return callback_.target<void()>() == callback.target<void()>(); });
}

AMULET_CORE_DLLX CancelManager::CancelManager()
    : detail::InternalCancelManager(cancel_mutex, cancelled, cancel_callbacks)
{
}

} // namespace Amulet
