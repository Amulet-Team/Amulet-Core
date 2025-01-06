#include <functional>
#include <list>
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

using CancelCallback = void (*)();

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

class VoidCancelManager : public virtual AbstractCancelManager {
public:
    void cancel() override;
    bool is_cancel_requested() override;
    void register_cancel_callback(CancelCallback callback) override;
    void unregister_cancel_callback(CancelCallback callback) override;
};

namespace detail {
    class InternalCancelManager : public virtual AbstractCancelManager {
    public:
        std::mutex& _cancel_mutex;
        bool& _cancelled;
        std::list<CancelCallback>& _cancel_callbacks;

        InternalCancelManager(
            std::mutex& cancel_mutex,
            bool& cancelled,
            std::list<CancelCallback>& cancel_callbacks);

        void cancel() override;
        bool is_cancel_requested() override;
        void register_cancel_callback(CancelCallback callback) override;
        void unregister_cancel_callback(CancelCallback callback) override;
    };
}

class CancelManager : public detail::InternalCancelManager {
private:
    std::mutex cancel_mutex;
    bool cancelled = false;
    std::list<CancelCallback> cancel_callbacks;

public:
    AMULET_CORE_DLLX CancelManager();
};

using ProgressCallback = void (*)(float);
using ProgressTextCallback = void (*)(const std::string&);

class AbstractProgressManager {
public:
    virtual ~AbstractProgressManager() = default;

    // Register a function to get called when progress changes.
    // The callback will be called from the thread `update_progress` is called in.
    virtual void register_progress_callback(ProgressCallback callback) = 0;

    // Unregister a registered function from being called when update_progress is called.
    virtual void unregister_progress_callback(ProgressCallback callback) = 0;

    // Notify the caller of the updated progress.
    // progress must be in the range 0.0 - 1.0
    virtual void update_progress(float progress) = 0;

    // Register a function to get called when progress changes.
    // The callback will be called from the thread `update_progress` is called in.
    virtual void register_progress_text_callback(ProgressTextCallback callback) = 0;

    // Unregister a registered function from being called when update_progress is called.
    virtual void unregister_progress_text_callback(ProgressTextCallback callback) = 0;

    // Send a new progress text to the caller.
    virtual void update_progress_text(const std::string& text) = 0;

    // Get a child ProgressManager.
    // If calling multiple functions, this allows segmenting the reported time.
    virtual std::unique_ptr<AbstractProgressManager> get_child(
        float progress_min, float progress_max)
        = 0;
};

class VoidProgressManager : public virtual AbstractProgressManager {
public:
    void register_progress_callback(ProgressCallback callback) override;
    void unregister_progress_callback(ProgressCallback callback) override;
    void update_progress(float progress) override;
    void register_progress_text_callback(ProgressTextCallback callback) override;
    void unregister_progress_text_callback(ProgressTextCallback callback) override;
    void update_progress_text(const std::string& text) override;
    std::unique_ptr<AbstractProgressManager> get_child(
        float progress_min, float progress_max) override;
};

namespace detail {
    class InternalProgressManager : public virtual AbstractProgressManager {
    public:
        std::mutex& _progress_mutex;
        std::list<ProgressCallback>& _progress_callbacks;
        std::list<ProgressTextCallback>& _progress_text_callbacks;
        float _progress_min;
        float _progress_max;

        InternalProgressManager(
            std::mutex& progress_mutex,
            std::list<ProgressCallback>& progress_callbacks,
            std::list<ProgressTextCallback>& progress_text_callbacks,
            float progress_min,
            float progress_max);

        void register_progress_callback(ProgressCallback callback) override;
        void unregister_progress_callback(ProgressCallback callback) override;
        void update_progress(float progress) override;
        void register_progress_text_callback(ProgressTextCallback callback) override;
        void unregister_progress_text_callback(ProgressTextCallback callback) override;
        void update_progress_text(const std::string& text) override;
        std::unique_ptr<AbstractProgressManager> get_child(
            float progress_min, float progress_max) override;
    };
}

class ProgressManager : public detail::InternalProgressManager {
private:
    std::mutex _progress_mutex;
    std::list<ProgressCallback> _progress_callbacks;
    std::list<ProgressTextCallback> _progress_text_callbacks;

public:
    AMULET_CORE_DLLX ProgressManager();
};

} // namespace Amulet
