#pragma once

#include <concepts>
#include <filesystem>
#include <functional>
#include <limits>
#include <map>
#include <memory>
#include <ranges>
#include <set>
#include <shared_mutex>
#include <vector>

#include <leveldb.hpp>

#include <amulet/utils/signal.hpp>
#include <amulet/utils/temp.hpp>
#include <amulet/utils/weak.hpp>

namespace Amulet {

class HistoryResource {
public:
    // The local index of the currently active revision.
    size_t index = 0;

    // The local index of the saved revision.
    // -1 if the index no longer exists (overwritten or destroyed future)
    size_t saved_index = 0;

    // The global history index the current state equates to.
    size_t global_index = 0;

    // Emitted when index changes during undo and redo.
    std::unique_ptr<Signal<>> changed;

    // Has the resource been changed since last save.
    bool has_changed()
    {
        return index != saved_index;
    }

    HistoryResource()
        : changed(std::make_unique<Signal<>>())
    {
    }
};

class AbstractHistoryManagerLayer;

namespace {
    class HistoryManagerPrivate {
    public:
        // Mutex to lock the state across multiple threads
        std::shared_mutex mutex;

        // The history layers that are part of this manager.
        WeakList<AbstractHistoryManagerLayer> layers;

        // The number of layers that have been created. Used as the id.
        size_t layer_count = 0;

        // A container tracking which resources have changed in each bin.
        std::vector<WeakSet<HistoryResource>> history_bins;

        // Which index is the current bin.
        size_t history_index = 0;

        TempDir db_path;

        std::unique_ptr<Amulet::LevelDB> db;

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

// The type of the layer identifier.
// 2^16 should be large enough but this can be increased if needed.
using LayerId = std::uint16_t;

// A group of resources in the history system.
template <ResourceId ResourceIdT>
class HistoryManagerLayer : public AbstractHistoryManagerLayer {
private:
    // Shared state.
    std::shared_ptr<HistoryManagerPrivate> _h;

    // A unique identifier for this layer.
    LayerId _id;

    // The resources in this layer.
    std::map<ResourceIdT, std::shared_ptr<HistoryResource>> _resources;

    HistoryManagerLayer(
        std::shared_ptr<HistoryManagerPrivate> h,
        LayerId id)
        : _h(h)
        , _id(id)
    {
    }

    friend HistoryManager;

protected:
    // Invalidate all future data.
    // Unique lock required.
    void invalidate_future() override
    {
        for (auto& [_, resource] : _resources) {
            if (resource->index < resource->saved_index) {
                resource->saved_index = -1;
            }
        }
    }

    // Destroy all resources in the layer.
    // Unique lock required.
    void reset() override
    {
        _resources.clear();
    }

    // Mark all resources as saved.
    // Unique lock required.
    void mark_saved() override
    {
        for (auto& [_, resource] : _resources) {
            resource->saved_index = resource->index;
        }
    }

public:
    // The public mutex.
    // Note the mutex is shared with the HistoryManager class.
    // Thread safe.
    std::shared_mutex& mutex()
    {
        return _h->mutex;
    }

    // View the resource data.
    // Shared or unique lock required while accessing the returned object.
    const std::map<ResourceIdT, std::shared_ptr<const HistoryResource>>& get_resources()
    {
        return _resources;
    }

    // Check if a resource entry exists.
    // If this is false the caller must call set_initial_resource
    // Shared or unique lock required.
    bool has_resource(ResourceIdT resource_id)
    {
        return _resources.contains(resource_id);
    }

    const HistoryResource& get_resource(ResourceIdT resource_id)
    {
        return _resources.at(resource_id);
    }

    // Get the current data for the resource.
    // Shared or unique lock required.
    std::string get_value(ResourceIdT resource_id)
    {
        throw std::runtime_error("NotImplementedError");
    }

    // Set the initial state for the resource.
    // If has_resource return false this must be called.
    // Unique lock required.
    void set_initial_value(ResourceIdT resource_id, std::string data)
    {
        throw std::runtime_error("NotImplementedError");
    }

    // Set the data for the resource.
    // Unique lock required.
    void set_value(ResourceIdT resource_id, std::string data)
    {
        throw std::runtime_error("NotImplementedError");
    }

    // Set the data for multiple resources.
    // Unique lock required.
    template <typename T>
        requires std::ranges::input_range<T>
        && std::same_as<
            std::ranges::range_value_t<T>,
            std::pair<ResourceIdT, std::string>>
    void set_values(T resources)
    {
        throw std::runtime_error("NotImplementedError");
    }
};

// The root history manager class.
class HistoryManager {
private:
    // Shared state.
    std::shared_ptr<HistoryManagerPrivate> _h;

public:
    HistoryManager();

    // The public mutex.
    // Note the mutex is shared with the HistoryManagerLayer class.
    // Thread safe.
    std::shared_mutex& mutex();

    // Get a new history layer.
    // Unique lock required.
    template <ResourceId ResourceIdT>
    std::shared_ptr<HistoryManagerLayer<ResourceIdT>> new_layer()
    {
        auto& layer_id = _h->layer_count;
        if (std::numeric_limits<LayerId>::max() < layer_id) {
            throw std::runtime_error("Exceeded the maximum number of layers (2^16)");
        }
        auto layer = std::make_shared<HistoryManagerLayer<ResourceIdT>>(_h, layer_id);
        _h->layers.push_back(layer);
        layer_id++;
        return layer;
    }

    // Reset all history data.
    // Unique lock required.
    void reset();

    // Mark the current state as the saved state.
    // Unique lock required.
    void mark_saved();

    // Create a new undo bin that new changes will be put in.
    // Unique lock required.
    void create_undo_bin();

    // Get the number of times undo can be called.
    // Shared or unique lock required.
    size_t get_undo_count();

    // Undo the changes made in the current bin.
    // Unique lock required.
    void undo();

    // Get the number of times redo can be called.
    // Shared or unique lock required.
    size_t get_redo_count();

    // Redo the changes in the next bin.
    // Unique lock required.
    void redo();
};

} // namespace Amulet
