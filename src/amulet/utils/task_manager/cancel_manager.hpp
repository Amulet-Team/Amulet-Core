#pragma once

#include <functional>
#include <list>
#include <memory>
#include <mutex>
#include <stdexcept>

#include <amulet/dll.hpp>

namespace Amulet {

// Exception to be raised by the callee when a task is cancelled.
class TaskCancelled : public std::exception {
private:
    std::string msg;

public:
    AMULET_CORE_DLLX TaskCancelled(std::string msg);
    AMULET_CORE_DLLX TaskCancelled();
    const char* what() const noexcept override;
};

using CancelCallback = std::function<void()>;

class AbstractCancelManager {
public:
    virtual ~AbstractCancelManager() = default;

    // Request the operation be canceled.
    // It is down to the operation to implement support for this.
    virtual void cancel() = 0;

    // Has cancel been called to signal that the operation should be canceled.
    virtual bool is_cancel_requested() = 0;

    // Register a function to get called when cancel is called.
    // The callback will be called from the thread `cancel` is called in.
    virtual void register_cancel_callback(CancelCallback callback) = 0;

    // Unregister a registered function from being called when cancel is called.
    virtual void unregister_cancel_callback(CancelCallback callback) = 0;
};

class VoidCancelManager : public AbstractCancelManager {
public:
    AMULET_CORE_DLLX VoidCancelManager() = default;
    AMULET_CORE_DLLX VoidCancelManager(const VoidCancelManager&) = default;
    void cancel() override;
    bool is_cancel_requested() override;
    void register_cancel_callback(CancelCallback callback) override;
    void unregister_cancel_callback(CancelCallback callback) override;
};

AMULET_CORE_DLLX extern VoidCancelManager global_VoidCancelManager;

class CancelManagerData {
public:
    std::mutex mutex;
    bool cancelled = false;
    std::list<CancelCallback> callbacks;
};

class CancelManager : public AbstractCancelManager {
private:
    std::shared_ptr<CancelManagerData> data;

public:
    AMULET_CORE_DLLX CancelManager(const std::shared_ptr<CancelManagerData>& data);
    AMULET_CORE_DLLX CancelManager();
    CancelManager(CancelManager&) = delete;

    void cancel() override;
    bool is_cancel_requested() override;
    void register_cancel_callback(CancelCallback callback) override;
    void unregister_cancel_callback(CancelCallback callback) override;
};

} // namespace Amulet
