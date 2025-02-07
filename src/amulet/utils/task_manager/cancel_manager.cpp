#include <functional>
#include <list>
#include <memory>
#include <mutex>
#include <stdexcept>

#include "cancel_manager.hpp"

namespace Amulet {

// VoidCancelManager
VoidCancelManager::VoidCancelManager() = default;
VoidCancelManager::VoidCancelManager(const VoidCancelManager&) = default;
VoidCancelManager::~VoidCancelManager() = default;
void VoidCancelManager::cancel() { }
bool VoidCancelManager::is_cancel_requested() { return false; }
void VoidCancelManager::register_cancel_callback(CancelCallback callback) { }
void VoidCancelManager::unregister_cancel_callback(CancelCallback callback) { }

VoidCancelManager global_VoidCancelManager;

// CancelManager
CancelManager::CancelManager() {}

void CancelManager::cancel()
{
    std::lock_guard<std::mutex> guard(mutex);
    if (cancelled) {
        return;
    }
    cancelled = true;
    for (const auto& callback : callbacks) {
        callback();
    }
}
bool CancelManager::is_cancel_requested()
{
    return cancelled;
}
void CancelManager::register_cancel_callback(CancelCallback callback)
{
    std::lock_guard<std::mutex> guard(mutex);
    // Add the callback to the end.
    callbacks.push_back(callback);
}
void CancelManager::unregister_cancel_callback(CancelCallback callback)
{
    std::lock_guard<std::mutex> guard(mutex);
    // Remove all callbacks matching the given callback.
    callbacks.remove_if(
        [&callback](CancelCallback callback_) { return callback_.target<void()>() == callback.target<void()>(); });
}

} // namespace Amulet
