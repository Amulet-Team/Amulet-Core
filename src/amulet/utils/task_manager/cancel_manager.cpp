#include <functional>
#include <list>
#include <memory>
#include <mutex>
#include <stdexcept>

#include "cancel_manager.hpp"
#include <amulet/utils/logging.hpp>

namespace Amulet {

// VoidCancelManager
VoidCancelManager::VoidCancelManager() = default;
VoidCancelManager::VoidCancelManager(const VoidCancelManager&) = default;
VoidCancelManager::~VoidCancelManager() = default;
void VoidCancelManager::cancel() { }
bool VoidCancelManager::is_cancel_requested() { return false; }
SignalToken<> VoidCancelManager::register_cancel_callback(CancelCallback callback) { 
    // Construct an empty token to keep the API consistent.
    return {};
}
void VoidCancelManager::unregister_cancel_callback(SignalToken<> token) { }

VoidCancelManager global_VoidCancelManager;

// CancelManager
CancelManager::CancelManager() { }

void CancelManager::cancel()
{
    {
        std::lock_guard lock(mutex);
        if (cancelled) {
            return;
        }
        cancelled = true;
    }
    signal.emit();
}
bool CancelManager::is_cancel_requested()
{
    return cancelled;
}
SignalToken<> CancelManager::register_cancel_callback(CancelCallback callback)
{
    return signal.connect(callback);
}
void CancelManager::unregister_cancel_callback(SignalToken<> token)
{
    signal.disconnect(token);
}

} // namespace Amulet
