#include <functional>
#include <list>
#include <memory>
#include <mutex>
#include <stdexcept>

#include <amulet/dll.hpp>

namespace Amulet {

using ProgressCallback = std::function<void(float)>;
using ProgressTextCallback = std::function<void(const std::string&)>;

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

class VoidProgressManager : public AbstractProgressManager {
public:
    AMULET_CORE_DLLX VoidProgressManager();
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
    class InternalProgressManager : public AbstractProgressManager {
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
