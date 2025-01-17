#include <functional>
#include <list>
#include <mutex>
#include <stdexcept>

#include "progress_manager.hpp"

namespace Amulet {

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

AMULET_CORE_DLLX ProgressManager::ProgressManager(const std::shared_ptr<ProgressManagerData>& data, float progress_min, float progress_max)
    : data(data)
    , _progress_min(progress_min)
    , _progress_max(progress_max)
{
}

AMULET_CORE_DLLX ProgressManager::ProgressManager()
    : ProgressManager(std::make_shared<ProgressManagerData>(), 0.0, 1.0)
{
}

void ProgressManager::register_progress_callback(ProgressCallback callback)
{
    std::lock_guard<std::mutex> guard(data->mutex);
    // Add the callback to the end.
    data->progress_callbacks.push_back(callback);
}

void ProgressManager::unregister_progress_callback(ProgressCallback callback)
{
    std::lock_guard<std::mutex> guard(data->mutex);
    // Remove all callbacks matching the given callback.
    data->progress_callbacks.remove_if(
        [&callback](ProgressCallback callback_) { return callback_.target<void(float)>() == callback.target<void(float)>(); });
}

void ProgressManager::update_progress(float progress)
{
    if (progress < 0.0 || 1.0 < progress) {
        throw std::runtime_error("progress must be between 0.0 and 1.0");
    }
    progress = _progress_min + progress * (_progress_max - _progress_min);
    std::lock_guard<std::mutex> guard(data->mutex);
    for (const auto& callback : data->progress_callbacks) {
        callback(progress);
    }
}

void ProgressManager::register_progress_text_callback(ProgressTextCallback callback)
{
    std::lock_guard<std::mutex> guard(data->mutex);
    // Add the callback to the end.
    data->progress_text_callbacks.push_back(callback);
}

void ProgressManager::unregister_progress_text_callback(ProgressTextCallback callback)
{
    std::lock_guard<std::mutex> guard(data->mutex);
    // Remove all callbacks matching the given callback.
    data->progress_text_callbacks.remove_if(
        [&callback](ProgressTextCallback callback_) { return callback_.target<void(const std::string&)>() == callback.target<void(const std::string&)>(); });
}

void ProgressManager::update_progress_text(const std::string& text)
{
    std::lock_guard<std::mutex> guard(data->mutex);
    for (const auto& callback : data->progress_text_callbacks) {
        callback(text);
    }
}

std::unique_ptr<AbstractProgressManager> ProgressManager::get_child(
    float progress_min, float progress_max)
{
    if (progress_min < 0.0 || 1.0 < progress_min) {
        throw std::runtime_error("progress_min must be between 0.0 and 1.0");
    }
    if (progress_max < 0.0 || 1.0 < progress_max) {
        throw std::runtime_error("progress_max must be between 0.0 and 1.0");
    }
    return std::make_unique<ProgressManager>(
        data,
        _progress_min + progress_min * (_progress_max - _progress_min),
        _progress_min + progress_max * (_progress_max - _progress_min));
}

} // namespace Amulet
