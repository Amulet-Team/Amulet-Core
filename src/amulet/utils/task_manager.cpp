#include <functional>
#include <list>
#include <mutex>
#include <stdexcept>

#include "task_manager.hpp"

namespace Amulet {

// Exception to be raised by the callee when a task is cancelled.
AMULET_CORE_DLLX TaskCancelled::TaskCancelled(std::string msg)
    : msg(msg)
{
}
AMULET_CORE_DLLX TaskCancelled::TaskCancelled()
    : TaskCancelled("Task Cancelled")
{
}
const char* TaskCancelled::what() const noexcept { return msg.c_str(); }

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
        [&callback](CancelCallback callback_) { return callback_ == callback; });
}

CancelManager::CancelManager()
    : detail::InternalCancelManager(cancel_mutex, cancelled, cancel_callbacks)
{
}

void VoidProgressManager::register_progress_callback(ProgressCallback callback) { }
void VoidProgressManager::unregister_progress_callback(ProgressCallback callback) { }
void VoidProgressManager::update_progress(float progress) { }
void VoidProgressManager::register_progress_text_callback(ProgressTextCallback callback) { }
void VoidProgressManager::unregister_progress_text_callback(ProgressTextCallback callback) { }
void VoidProgressManager::update_progress_text(const std::string& text) { }
std::unique_ptr<AbstractProgressManager> VoidProgressManager::get_child(
    float progress_min, float progress_max)
{
    return std::make_unique<VoidProgressManager>(*this);
}

detail::InternalProgressManager::InternalProgressManager(
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

void detail::InternalProgressManager::register_progress_callback(ProgressCallback callback)
{
    std::lock_guard<std::mutex> guard(_progress_mutex);
    // Add the callback to the end.
    _progress_callbacks.push_back(callback);
}

void detail::InternalProgressManager::unregister_progress_callback(ProgressCallback callback)
{
    std::lock_guard<std::mutex> guard(_progress_mutex);
    // Remove all callbacks matching the given callback.
    _progress_callbacks.remove_if(
        [&callback](ProgressCallback callback_) { return callback_ == callback; });
}

void detail::InternalProgressManager::update_progress(float progress)
{
    if (progress < 0.0 || 1.0 < progress) {
        throw std::runtime_error("progress must be between 0.0 and 1.0");
    }
    progress = _progress_min + progress * (_progress_max - _progress_min);
    std::lock_guard<std::mutex> guard(_progress_mutex);
    for (const auto& callback : _progress_callbacks) {
        callback(progress);
    }
}

void detail::InternalProgressManager::register_progress_text_callback(ProgressTextCallback callback)
{
    std::lock_guard<std::mutex> guard(_progress_mutex);
    // Add the callback to the end.
    _progress_text_callbacks.push_back(callback);
}

void detail::InternalProgressManager::unregister_progress_text_callback(ProgressTextCallback callback)
{
    std::lock_guard<std::mutex> guard(_progress_mutex);
    // Remove all callbacks matching the given callback.
    _progress_text_callbacks.remove_if(
        [&callback](ProgressTextCallback callback_) { return callback_ == callback; });
}

void detail::InternalProgressManager::update_progress_text(const std::string& text)
{
    std::lock_guard<std::mutex> guard(_progress_mutex);
    for (const auto& callback : _progress_text_callbacks) {
        callback(text);
    }
}

std::unique_ptr<AbstractProgressManager> detail::InternalProgressManager::get_child(
    float progress_min, float progress_max)
{
    if (progress_min < 0.0 || 1.0 < progress_min) {
        throw std::runtime_error("progress_min must be between 0.0 and 1.0");
    }
    if (progress_max < 0.0 || 1.0 < progress_max) {
        throw std::runtime_error("progress_max must be between 0.0 and 1.0");
    }
    return std::make_unique<detail::InternalProgressManager>(
        _progress_mutex,
        _progress_callbacks,
        _progress_text_callbacks,
        _progress_min + progress_min * (_progress_max - _progress_min),
        _progress_min + progress_max * (_progress_max - _progress_min));
}

AMULET_CORE_DLLX ProgressManager::ProgressManager()
    : detail::InternalProgressManager(_progress_mutex, _progress_callbacks, _progress_text_callbacks, 0.0, 1.0)
{
}

detail::InternalTaskManager::InternalTaskManager(
    std::mutex& cancel_mutex,
    bool& cancelled,
    std::list<CancelCallback>& cancel_callbacks,
    std::mutex& progress_mutex,
    std::list<ProgressCallback>& progress_callbacks,
    std::list<ProgressTextCallback>& progress_text_callbacks,
    float progress_min,
    float progress_max)
    : detail::InternalCancelManager(cancel_mutex, cancelled, cancel_callbacks)
    , detail::InternalProgressManager(progress_mutex, progress_callbacks, progress_text_callbacks, progress_min, progress_max)
{
}

std::unique_ptr<AbstractProgressManager> detail::InternalTaskManager::get_child(
    float progress_min, float progress_max)
{
    if (progress_min < 0.0 || 1.0 < progress_min) {
        throw std::runtime_error("progress_min must be between 0.0 and 1.0");
    }
    if (progress_max < 0.0 || 1.0 < progress_max) {
        throw std::runtime_error("progress_max must be between 0.0 and 1.0");
    }
    return std::make_unique<detail::InternalTaskManager>(
        _cancel_mutex,
        _cancelled,
        _cancel_callbacks,
        _progress_mutex,
        _progress_callbacks,
        _progress_text_callbacks,
        _progress_min + progress_min * (_progress_max - _progress_min),
        _progress_min + progress_max * (_progress_max - _progress_min));
}

AMULET_CORE_DLLX TaskManager::TaskManager()
    : detail::InternalTaskManager(
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

} // namespace Amulet
