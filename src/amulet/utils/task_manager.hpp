#include <functional>
#include <mutex>
#include <stdexcept>

namespace Amulet {

// Exception to be raised by the callee when a task is cancelled.
class TaskCancelled : public std::exception {
private:
    std::string msg;

public:
    TaskCancelled(std::string msg)
        : msg(msg)
    {
    }
    TaskCancelled()
        : TaskCancelled("Task Cancelled")
    {
    }
    const char* what() const noexcept override { return msg.c_str(); }
};

using CancelCallback = void (*)();

class AbstractCancelManager {
public:
    virtual ~AbstractCancelManager() { }

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
    void cancel() override { }
    bool is_cancel_requested() override { return false; }
    virtual void register_cancel_callback(CancelCallback callback) override {};
    virtual void unregister_cancel_callback(CancelCallback callback) override {};
};

class _CancelManager : public AbstractCancelManager {
protected:
    std::mutex& _cancel_mutex;
    bool& _cancelled;
    std::list<CancelCallback>& _cancel_callbacks;

    _CancelManager(
        std::mutex& cancel_mutex,
        bool& cancelled,
        std::list<CancelCallback>& cancel_callbacks)
        : _cancelled(cancelled)
        , _cancel_mutex(cancel_mutex)
        , _cancel_callbacks(cancel_callbacks)
    {
    }

public:
    void cancel() override
    {
        std::lock_guard guard(_cancel_mutex);
        _cancelled = true;
        for (const auto& callback : _cancel_callbacks) {
            callback();
        }
    }
    bool is_cancel_requested() override
    {
        return _cancelled;
    }
    virtual void register_cancel_callback(CancelCallback callback) override
    {
        std::lock_guard guard(_cancel_mutex);
        // Add the callback to the end.
        _cancel_callbacks.push_back(callback);
    };
    virtual void unregister_cancel_callback(CancelCallback callback) override
    {
        std::lock_guard guard(_cancel_mutex);
        // Remove all callbacks matching the given callback.
        _cancel_callbacks.remove_if(
            [&callback](CancelCallback callback_) { return callback_ == callback; });
    };
};

class CancelManager : public _CancelManager {
private:
    std::mutex cancel_mutex;
    bool cancelled = false;
    std::list<CancelCallback> cancel_callbacks;

public:
    CancelManager()
        : _CancelManager(cancel_mutex, cancelled, cancel_callbacks)
    {
    }
};

using ProgressCallback = void (*)(float);
using ProgressTextCallback = void (*)(const std::string&);

class AbstractProgressManager {
public:
    virtual ~AbstractProgressManager() {};

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
    virtual std::unique_ptr<AbstractProgressManager> get_child(float progress_min, float progress_max) = 0;
};

class VoidProgressManager : public AbstractProgressManager {
public:
    virtual void register_progress_callback(ProgressCallback callback) override { }
    virtual void unregister_progress_callback(ProgressCallback callback) override { }
    virtual void update_progress(float progress) override { }
    virtual void register_progress_text_callback(ProgressTextCallback callback) override { }
    virtual void unregister_progress_text_callback(ProgressTextCallback callback) override { }
    virtual void update_progress_text(const std::string& text) override { }
    virtual std::unique_ptr<AbstractProgressManager> get_child(
        float progress_min, float progress_max) override
    {
        return std::make_unique<VoidProgressManager>(this);
    }
};

class _ProgressManager : public AbstractProgressManager {
protected:
    std::mutex& _progress_mutex;
    std::list<ProgressCallback>& _progress_callbacks;
    std::list<ProgressTextCallback>& _progress_text_callbacks;
    float _progress_min;
    float _progress_max;

    _ProgressManager(
        std::mutex& progress_mutex,
        std::list<ProgressCallback>& progress_callbacks,
        std::list<ProgressTextCallback>& progress_text_callbacks,
        float progress_min,
        float progress_max)
        : _progress_mutex(progress_mutex)
        , _progress_callbacks(progress_callbacks)
        , _progress_text_callbacks(progress_text_callbacks)
        , _progress_min(progress_min)
        , _progress_max(progress_max)
    {
    }

public:
    virtual void register_progress_callback(ProgressCallback callback) override
    {
        std::lock_guard guard(_progress_mutex);
        // Add the callback to the end.
        _progress_callbacks.push_back(callback);
    }

    virtual void unregister_progress_callback(ProgressCallback callback) override
    {
        std::lock_guard guard(_progress_mutex);
        // Remove all callbacks matching the given callback.
        _progress_callbacks.remove_if(
            [&callback](ProgressCallback callback_) { return callback_ == callback; });
    }

    virtual void update_progress(float progress) override
    {
        if (progress < 0.0 || 1.0 < progress) {
            throw std::runtime_error("progress must be between 0.0 and 1.0");
        }
        progress = _progress_min + progress * (_progress_max - _progress_min);
        std::lock_guard guard(_progress_mutex);
        for (const auto& callback : _progress_callbacks) {
            callback(progress);
        }
    }

    virtual void register_progress_text_callback(ProgressTextCallback callback) override
    {
        std::lock_guard guard(_progress_mutex);
        // Add the callback to the end.
        _progress_text_callbacks.push_back(callback);
    }

    virtual void unregister_progress_text_callback(ProgressTextCallback callback) override
    {
        std::lock_guard guard(_progress_mutex);
        // Remove all callbacks matching the given callback.
        _progress_text_callbacks.remove_if(
            [&callback](ProgressTextCallback callback_) { return callback_ == callback; });
    }

    virtual void update_progress_text(const std::string& text) override
    {
        std::lock_guard guard(_progress_mutex);
        for (const auto& callback : _progress_text_callbacks) {
            callback(text);
        }
    }

    virtual std::unique_ptr<AbstractProgressManager> get_child(
        float progress_min, float progress_max) override
    {
        if (progress_min < 0.0 || 1.0 < progress_min) {
            throw std::runtime_error("progress_min must be between 0.0 and 1.0");
        }
        if (progress_max < 0.0 || 1.0 < progress_max) {
            throw std::runtime_error("progress_max must be between 0.0 and 1.0");
        }
        return std::make_unique<_ProgressManager>(
            _progress_mutex,
            _progress_callbacks,
            _progress_text_callbacks,
            _progress_min + progress_min * (_progress_max - _progress_min),
            _progress_min + progress_max * (_progress_max - _progress_min));
    }
};

class ProgressManager : public _ProgressManager {
private:
    std::mutex _progress_mutex;
    std::list<ProgressCallback> _progress_callbacks;
    std::list<ProgressTextCallback> _progress_text_callbacks;

public:
    ProgressManager()
        : _ProgressManager(_progress_mutex, _progress_callbacks, _progress_text_callbacks, 0.0, 1.0)
    {
    }
};

class AbstractTaskManager : public AbstractCancelManager, public AbstractProgressManager { };

// An empty TaskManager that ignores all calls.
class VoidTaskManager : public VoidCancelManager, public VoidProgressManager, public AbstractTaskManager { };

class _TaskManager : public _CancelManager, public _ProgressManager, public AbstractTaskManager {
protected:
    _TaskManager(
        std::mutex& cancel_mutex,
        bool& cancelled,
        std::list<CancelCallback>& cancel_callbacks,
        std::mutex& progress_mutex,
        std::list<ProgressCallback>& progress_callbacks,
        std::list<ProgressTextCallback>& progress_text_callbacks,
        float progress_min,
        float progress_max)
        : _CancelManager(cancelled, cancel_mutex, cancel_callbacks)
        , _ProgressManager(progress_mutex, progress_callbacks, progress_text_callbacks, progress_min, progress_max)
    {
    }

public:
    virtual std::unique_ptr<AbstractProgressManager> get_child(
        float progress_min, float progress_max) override
    {
        if (progress_min < 0.0 || 1.0 < progress_min) {
            throw std::runtime_error("progress_min must be between 0.0 and 1.0");
        }
        if (progress_max < 0.0 || 1.0 < progress_max) {
            throw std::runtime_error("progress_max must be between 0.0 and 1.0");
        }
        return std::make_unique<_TaskManager>(
            _cancel_mutex,
            _cancelled,
            _cancel_callbacks,
            _progress_mutex,
            _progress_callbacks,
            _progress_text_callbacks,
            _progress_min + progress_min * (_progress_max - _progress_min),
            _progress_min + progress_max * (_progress_max - _progress_min));
    }
};

class TaskManager : public _TaskManager {
private:
    std::mutex cancel_mutex;
    bool cancelled = false;
    std::list<CancelCallback> cancel_callbacks;
    std::mutex _progress_mutex;
    std::list<ProgressCallback> _progress_callbacks;
    std::list<ProgressTextCallback> _progress_text_callbacks;

public:
    TaskManager()
        : _TaskManager(
              cancel_mutex,
              cancelled,
              cancel_callbacks,
              _progress_mutex,
              _progress_callbacks,
              _progress_text_callbacks,
              0.0,
              1.0)
    {
    }
};

} // namespace Amulet
