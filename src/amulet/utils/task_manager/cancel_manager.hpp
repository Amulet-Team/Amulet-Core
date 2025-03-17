#pragma once

#include <functional>
#include <list>
#include <memory>
#include <mutex>
#include <stdexcept>

#include <amulet/dll.hpp>
#include <amulet/utils/signal.hpp>

namespace Amulet {

// Exception to be raised by the callee when a task is cancelled.
class AMULET_CORE_EXPORT_EXCEPTION TaskCancelled : public std::exception {
private:
    std::string msg;

public:
    // Constructors
    explicit TaskCancelled(const std::string& msg)
        : msg(msg.c_str())
    {
    }
    TaskCancelled()
        : TaskCancelled("Task Cancelled")
    {
    }
    const char* what() const noexcept override
    {
        return msg.c_str();
    }
};

using CancelCallback = std::function<void()>;

class AbstractCancelManager {
public:
    virtual ~AbstractCancelManager() = default;

    // Request the operation be cancelled.
    // It is down to the operation to implement support for this.
    // Thread safe.
    virtual void cancel() = 0;

    // Has cancel been called to signal that the operation should be cancelled.
    // Thread safe.
    virtual bool is_cancel_requested() = 0;

    // Register a function to get called when cancel is called.
    // The callback will be called from the thread `cancel` is called in.
    // Thread safe.
    virtual SignalToken<> register_cancel_callback(CancelCallback callback) = 0;

    // Unregister a registered function from being called when cancel is called.
    // Thread safe.
    virtual void unregister_cancel_callback(SignalToken<> token) = 0;
};

class VoidCancelManager : public AbstractCancelManager {
public:
    AMULET_CORE_EXPORT VoidCancelManager();
    AMULET_CORE_EXPORT VoidCancelManager(const VoidCancelManager&);
    AMULET_CORE_EXPORT ~VoidCancelManager() override;
    AMULET_CORE_EXPORT void cancel() override;
    AMULET_CORE_EXPORT bool is_cancel_requested() override;
    AMULET_CORE_EXPORT SignalToken<> register_cancel_callback(CancelCallback callback) override;
    AMULET_CORE_EXPORT void unregister_cancel_callback(SignalToken<> token) override;
};

AMULET_CORE_EXPORT extern VoidCancelManager global_VoidCancelManager;

class CancelManager : public AbstractCancelManager {
private:
    std::mutex mutex;
    bool cancelled = false;
    Signal<> signal;

public:
    AMULET_CORE_EXPORT CancelManager();
    CancelManager(CancelManager&) = delete;

    AMULET_CORE_EXPORT void cancel() override;
    AMULET_CORE_EXPORT bool is_cancel_requested() override;
    AMULET_CORE_EXPORT SignalToken<> register_cancel_callback(CancelCallback callback) override;
    AMULET_CORE_EXPORT void unregister_cancel_callback(SignalToken<> token) override;
};

} // namespace Amulet
