#pragma once

#include <concepts>
#include <limits>
#include <map>
#include <memory>
#include <ranges>
#include <set>
#include <shared_mutex>
#include <vector>

#include <amulet/utils/signal.hpp>

namespace Amulet {

struct HistoryResource {
    // The local index of the currently active revision.
    size_t index = 0;

    // The local index of the saved revision.
    // -1 if the index no longer exists (overwritten or destroyed future)
    size_t saved_index = 0;

    // The global history index the current state equates to.
    size_t global_index = 0;
};

class AbstractHistoryManagerLayer;

namespace {

    class HistoryManagerPrivate {
    public:
        // Mutex to lock the state across multiple threads
        std::shared_mutex mutex;

        // The history layers that are part of this manager.
        std::vector<std::weak_ptr<AbstractHistoryManagerLayer>> layers;

        // A container tracking which resources have changed in each bin.
        std::vector<std::set<std::shared_ptr<HistoryResource>>> history_bins;
        
        // Which index is the current bin.
        size_t history_index = 0;

        HistoryManagerPrivate();

        // Destroy all future redo bins.
        void invalidate_future();

        // Are there bins ahead of the history index.
        bool has_redo();
    };

} // namespace

class HistoryManager;

class AbstractHistoryManagerLayer {
protected:
    // Destroy all future redo bins.
    // Unique mutex required.
    virtual void invalidate_future() = 0;

    // Reset all history data.
    // Unique mutex required.
    virtual void reset() = 0;

    // Notify the layer that the data has been saved.
    // Unique mutex required.
    virtual void mark_saved() = 0;

    friend HistoryManagerPrivate;
    friend HistoryManager;
};

template <typename T>
concept ResourceId = std::totally_ordered<T> && std::convertible_to<T, std::string>;

using LayerId = std::uint16_t;

template <ResourceId ResourceIdT>
class HistoryManagerLayer {
private:
    std::shared_ptr<HistoryManagerPrivate> _h;
    std::string _uuid;
    std::map<ResourceIdT, HistoryResource> _resources;

    HistoryManagerLayer(
        std::shared_ptr<HistoryManagerPrivate>,
        LayerId id);

    friend HistoryManager;

protected:
    void invalidate_future() override
    {
        for (auto& [_, resource] : _resources) {
            if (resource.index < resource.saved_index) {
                resource.saved_index = -1;
            }
        }
    }
    void reset() override
    {
        _resources.clear();
    }
    void mark_saved() override
    {
        for (auto& [_, resource] : _resources) {
            resource.saved_index = resource.index;
        }
    }

public:
    // const std::map<ResourceIdT, HistoryResource>& get_resources()
    //{
    //     return _resources
    // }

    // Check if a resource entry exists.
    // If this is false the caller must call set_initial_resource
    bool has_resource(ResourceIdT resource_id)
    {
        return _resources.contains(resource_id);
    }

    // Get the current data for the resource.
    std::string get_resource(ResourceIdT resource_id)
    {
        throw std::runtime_error("NotImplementedError");
    }

    // Set the initial state for the resource.
    // If has_resource return false this must be called.
    void set_initial_resource(ResourceIdT resource_id, std::string data)
    {
        throw std::runtime_error("NotImplementedError");
    }

    // Set the data for the resource.
    void set_resource(ResourceIdT resource_id, std::string data)
    {
        throw std::runtime_error("NotImplementedError");
    }

    // Set the data for multiple resources.
    void set_resources(std::input_range<const std::pair<ResourceIdT, std::string>> resources)
    {
        throw std::runtime_error("NotImplementedError");
    }
};

class HistoryManager {
private:
    std::shared_ptr<HistoryManagerPrivate> _h;

public:
    HistoryManager();

    template <ResourceId ResourceIdT>
    std::shared_ptr<HistoryManagerLayer<ResourceIdT>> new_layer()
    {
        auto layer_id = _h->layers.size();
        if (std::numeric_limits<LayerId>::max() < layer_id) {
            throw std::runtime_error("Exceeded the maximum number of layers (2^16)");
        }
        auto layer = std::make_shared<HistoryManagerLayer<ResourceIdT>>(_h, layer_id);
        _h->layers.push_back(layer);
        return layer;
    }

    // Reset all history data.
    void reset();

    // Mark the current state as the saved state.
    void mark_saved();

    // Create a new undo bin that new changes will be put in.
    void create_undo_bin();

    // Get the number of times undo can be called.
    size_t get_undo_count();

    // Undo the changes made in the current bin.
    void undo();

    // Get the number of times redo can be called.
    size_t get_redo_count();

    // Redo the changes in the next bin.
    void redo();
};

} // namespace Amulet
