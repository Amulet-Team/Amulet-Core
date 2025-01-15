#include <functional>
#include <list>
#include <memory>
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

VoidCancelManager global_VoidCancelManager;

AMULET_CORE_DLLX CancelManager::CancelManager(const std::shared_ptr<CancelManagerData>& data)
    : data(data)
{
}

AMULET_CORE_DLLX CancelManager::CancelManager()
    : CancelManager(std::make_shared<CancelManagerData>())
{
}

void CancelManager::cancel()
{
    std::lock_guard<std::mutex> guard(data->mutex);
    if (data->cancelled) {
        return;
    }
    data->cancelled = true;
    for (const auto& callback : data->callbacks) {
        callback();
    }
}
bool CancelManager::is_cancel_requested()
{
    return data->cancelled;
}
void CancelManager::register_cancel_callback(CancelCallback callback)
{
    std::lock_guard<std::mutex> guard(data->mutex);
    // Add the callback to the end.
    data->callbacks.push_back(callback);
}
void CancelManager::unregister_cancel_callback(CancelCallback callback)
{
    std::lock_guard<std::mutex> guard(data->mutex);
    // Remove all callbacks matching the given callback.
    data->callbacks.remove_if(
        [&callback](CancelCallback callback_) { return callback_.target<void()>() == callback.target<void()>(); });
}

} // namespace Amulet
