#include <functional>
#include <list>
#include <mutex>
#include <stdexcept>

#include "progress_manager.hpp"

namespace Amulet {

AMULET_CORE_DLLX VoidProgressManager::VoidProgressManager() { }
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
        [&callback](ProgressCallback callback_) { return callback_.target<void(float)>() == callback.target<void(float)>(); });
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
        [&callback](ProgressTextCallback callback_) { return callback_.target<void(const std::string&)>() == callback.target<void(const std::string&)>(); });
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

} // namespace Amulet
