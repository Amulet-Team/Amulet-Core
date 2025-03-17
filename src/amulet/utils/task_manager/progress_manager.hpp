#pragma once

#include <functional>
#include <list>
#include <memory>
#include <mutex>
#include <stdexcept>

#include <amulet/dll.hpp>
#include <amulet/utils/signal.hpp>

namespace Amulet {

using ProgressCallback = std::function<void(float)>;
using ProgressTextCallback = std::function<void(const std::string&)>;

class AbstractProgressManager {
public:
    virtual ~AbstractProgressManager() = default;

    // Register a function to get called when progress changes.
    // The callback will be called from the thread `update_progress` is called in.
    // Thread safe.
    virtual SignalToken<float> register_progress_callback(ProgressCallback callback) = 0;

    // Unregister a registered function from being called when update_progress is called.
    // Thread safe.
    virtual void unregister_progress_callback(SignalToken<float> token) = 0;

    // Notify the caller of the updated progress.
    // progress must be in the range 0.0 - 1.0
    // Thread safe.
    virtual void update_progress(float progress) = 0;

    // Register a function to get called when progress changes.
    // The callback will be called from the thread `update_progress` is called in.
    // Thread safe.
    virtual SignalToken<std::string> register_progress_text_callback(ProgressTextCallback callback) = 0;

    // Unregister a registered function from being called when update_progress is called.
    // Thread safe.
    virtual void unregister_progress_text_callback(SignalToken<std::string> token) = 0;

    // Send a new progress text to the caller.
    // Thread safe.
    virtual void update_progress_text(const std::string& text) = 0;

    // Get a child ProgressManager.
    // If calling multiple functions, this allows segmenting the reported time.
    // Thread safe.
    virtual std::unique_ptr<AbstractProgressManager> get_child(
        float progress_min, float progress_max)
        = 0;
};

class VoidProgressManager : public AbstractProgressManager {
public:
    AMULET_CORE_EXPORT VoidProgressManager() = default;
    AMULET_CORE_EXPORT VoidProgressManager(VoidProgressManager&) = default;
    SignalToken<float> register_progress_callback(ProgressCallback callback) override;
    void unregister_progress_callback(SignalToken<float> token) override;
    void update_progress(float progress) override;
    SignalToken<std::string> register_progress_text_callback(ProgressTextCallback callback) override;
    void unregister_progress_text_callback(SignalToken<std::string> token) override;
    void update_progress_text(const std::string& text) override;
    std::unique_ptr<AbstractProgressManager> get_child(
        float progress_min, float progress_max) override;
};

class ProgressManagerData {
public:
    Signal<float> progress_changed;
    Signal<std::string> progress_text_changed;
};

class ProgressManager : public AbstractProgressManager {
private:
    std::shared_ptr<ProgressManagerData> data;
    float _progress_min;
    float _progress_max;

public:
    AMULET_CORE_EXPORT ProgressManager(const std::shared_ptr<ProgressManagerData>& data, float progress_min, float progress_max);
    AMULET_CORE_EXPORT ProgressManager();
    ProgressManager(ProgressManager&) = delete;

    SignalToken<float> register_progress_callback(ProgressCallback callback) override;
    void unregister_progress_callback(SignalToken<float> token) override;
    void update_progress(float progress) override;
    SignalToken<std::string> register_progress_text_callback(ProgressTextCallback callback) override;
    void unregister_progress_text_callback(SignalToken<std::string> token) override;
    void update_progress_text(const std::string& text) override;
    std::unique_ptr<AbstractProgressManager> get_child(
        float progress_min, float progress_max) override;
};

} // namespace Amulet
