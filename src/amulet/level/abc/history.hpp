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
#include <leveldb/write_batch.h>

#include <amulet/dll.hpp>
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
    bool has_changed() const
    {
        return index != saved_index;
    }

    HistoryResource()
        : changed(std::make_unique<Signal<>>())
    {
    }
};

class AbstractHistoryManagerLayer;

namespace detail {
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

        AMULET_CORE_EXPORT HistoryManagerPrivate();

        // Destroy all future redo bins.
        AMULET_CORE_EXPORT void invalidate_future();

        // Are there bins ahead of the history index.
        AMULET_CORE_EXPORT bool has_redo();
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

    friend detail::HistoryManagerPrivate;
    friend HistoryManager;
};

template <typename T>
concept ResourceId = std::totally_ordered<T> && std::convertible_to<T, std::string>;

// The type of the layer identifier.
// 2^16 should be large enough but this can be increased if needed.
using LayerId = std::uint16_t;

template <ResourceId ResourceIdT>
std::string get_resource_key(LayerId id, const ResourceIdT& resource_id, size_t index)
{
    std::string key;
    key.reserve(32);
    key.append(reinterpret_cast<char*>(&id), sizeof(LayerId));
    key.push_back('/');
    key.append(resource_id);
    key.push_back('/');
    key.append(reinterpret_cast<char*>(&index), sizeof(size_t));
    return key;
}

// Rule to use if the resource has not been created when setting it.
enum class HistoryInitialisationMode {
    Error, // Throw std::runtime_error if set_initial_value has not been called.
    Empty, // Call set_initial_value with an empty value.
    Value // Call set_initial_value with the given value.
};

// A group of resources in the history system.
template <ResourceId ResourceIdT>
class HistoryManagerLayer : public AbstractHistoryManagerLayer {
private:
    // Shared state.
    std::shared_ptr<detail::HistoryManagerPrivate> _h;

    // A unique identifier for this layer.
    LayerId _id;

    // The resources in this layer.
    std::map<ResourceIdT, std::shared_ptr<HistoryResource>> _resources;

    HistoryManagerLayer(
        std::shared_ptr<detail::HistoryManagerPrivate> h,
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
    std::shared_mutex& get_mutex()
    {
        return _h->mutex;
    }

    // View the resource data.
    // The caller must not modify the HistoryResource state.
    // Shared or unique lock required while accessing the returned object.
    const std::map<ResourceIdT, std::shared_ptr<HistoryResource>>& get_resources()
    {
        return _resources;
    }

    // Check if a resource entry exists.
    // If this is false the caller must call set_initial_resource
    // Shared or unique lock required.
    bool has_resource(const ResourceIdT& resource_id) const
    {
        return _resources.contains(resource_id);
    }

    // Get the HistoryResource instance for this resource.
    // External shared lock required.
    const HistoryResource& get_resource(const ResourceIdT& resource_id) const
    {
        return *_resources.at(resource_id);
    }

    // Get the current data for the resource.
    // Shared or unique lock required.
    std::string get_value(const ResourceIdT& resource_id) const
    {
        // Get the resource
        const auto& resource = *_resources.at(resource_id);
        // Get the value
        std::string value;
        auto& db = *_h->db;
        auto status = db->Get(
            db.get_read_options(),
            get_resource_key(_id, resource_id, resource.index),
            &value);
        if (!status.ok()) {
            throw std::runtime_error(status.ToString());
        }
        return value;
    }

private:
    std::map<ResourceIdT, std::shared_ptr<HistoryResource>>::iterator _set_initial_value(const ResourceIdT& resource_id, const std::string& value)
    {
        // Write the value to the database
        auto& db = *_h->db;
        auto status = db->Put(
            db.get_write_options(),
            get_resource_key(_id, resource_id, 0),
            value);
        if (!status.ok()) {
            throw std::runtime_error(status.ToString());
        }
        // Create the resource
        return _resources.emplace(resource_id, std::make_shared<HistoryResource>()).first;
    }

public:
    // Set the initial state for the resource.
    // If has_resource returns false this must be called.
    // Unique lock required.
    void set_initial_value(const ResourceIdT& resource_id, const std::string& value)
    {
        // Check that it doesn't already exist.
        if (_resources.contains(resource_id)) {
            throw std::runtime_error("Resource already exists. " + std::string(resource_id));
        }
        _set_initial_value(resource_id, value);
    }

    // Set the data for the resource.
    // init_mode can be set to configure what happens if set_initial_value has not been called for this resource.
    // Unique lock required.
    template <HistoryInitialisationMode init_mode = HistoryInitialisationMode::Error>
    void set_value(const ResourceIdT& resource_id, const std::string& value)
    {
        // A change has been made. Invalidate all future undo points.
        _h->invalidate_future();

        // Get the resource
        auto it = _resources.find(resource_id);
        if (it == _resources.end()) {
            // Resource does not exist.
            if constexpr (init_mode == HistoryInitialisationMode::Error) {
                throw std::runtime_error("Initial value has not been set for resource: " + std::string(resource_id));
            } else if constexpr (init_mode == HistoryInitialisationMode::Empty) {
                it = _set_initial_value(resource_id, "");
                it->second->saved_index = -1;
            } else {
                static_assert(init_mode == HistoryInitialisationMode::Value);
                it = _set_initial_value(resource_id, value);
                it->second->saved_index = -1;
                return; // There is no point setting it again.
            }
        }
        auto resource_ptr = it->second;
        auto& resource = *resource_ptr;

        // Update the resource state
        if (resource.global_index != _h->history_index) {
            // A new global bin has been created since this was last changed.
            // Create a new local bin.
            resource.index++;
            resource.global_index = _h->history_index;
        }
        if (resource.index == resource.saved_index) {
            // We are modifying the saved bin.
            // The saved index is invalid.
            resource.saved_index = -1;
        }
        // Write to the database.
        auto& db = *_h->db;
        auto status = db->Put(
            db.get_write_options(),
            get_resource_key(_id, resource_id, resource.index),
            value);
        if (!status.ok()) {
            throw std::runtime_error(status.ToString());
        }
        if (_h->history_index != 0) {
            // Add the resource to the global bin
            _h->history_bins.at(_h->history_index).emplace(resource_ptr);
        }
    }

    // Set the data for multiple resources.
    // Supports any range of pair-like elements. Elements must remain valid beyond the life of the iterator.
    // init_mode can be set to configure what happens if set_initial_value has not been called for this resource.
    // Unique lock required.
    template <HistoryInitialisationMode init_mode = HistoryInitialisationMode::Error, typename T>
        requires std::ranges::forward_range<T>
        && std::convertible_to<
            std::ranges::range_value_t<T>,
            const std::pair<ResourceIdT, std::string>>
    void set_values(const T& resources)
    {
        // A change has been made. Invalidate all future undo points.
        _h->invalidate_future();

        // Get all resources.
        // If a resource doesn't exist we should error before changing the state.
        std::list<std::tuple<const ResourceIdT&, const std::string&, std::shared_ptr<HistoryResource>>> resource_data;
        for (const auto& [resource_id, value] : resources) {
            auto it = _resources.find(resource_id);
            if (it == _resources.end()) {
                // Resource does not exist.
                if constexpr (init_mode == HistoryInitialisationMode::Error) {
                    throw std::runtime_error("Initial value has not been set for resource: " + std::string(resource_id));
                } else if constexpr (init_mode == HistoryInitialisationMode::Empty) {
                    const auto& resource_ptr = _set_initial_value(resource_id, "")->second;
                    resource_ptr->saved_index = -1;
                    resource_data.emplace_back(resource_id, value, resource_ptr);
                } else {
                    static_assert(init_mode == HistoryInitialisationMode::Value);
                    // Set the original state and don't add it to resource_data.
                    it = _set_initial_value(resource_id, value);
                    it->second->saved_index = -1;
                }
            } else {
                resource_data.emplace_back(resource_id, value, it->second);
            }
        }

        // skip if there are no resources to add
        if (resource_data.empty()) {
            return;
        }

        // Create the write batch
        leveldb::WriteBatch batch;

        for (const auto& [resource_id, value, resource_ptr] : resource_data) {
            // Get the resource
            auto& resource = *resource_ptr;

            // Update the resource state
            if (resource.global_index != _h->history_index) {
                // A new global bin has been created since this was last changed.
                // Create a new local bin.
                resource.index++;
                resource.global_index = _h->history_index;
            }
            if (resource.index == resource.saved_index) {
                // We are modifying the saved bin.
                // The saved index is invalid.
                resource.saved_index = -1;
            }

            // Add to the batch
            batch.Put(
                get_resource_key(_id, resource_id, resource.index),
                value);
        }

        // Write to the database.
        auto& db = *_h->db;
        auto status = db->Write(
            db.get_write_options(),
            &batch);
        if (!status.ok()) {
            throw std::runtime_error(status.ToString());
        }
        if (_h->history_index != 0) {
            // Add the resources to the global bin
            auto& bin = _h->history_bins.at(_h->history_index);
            for (const auto& data : resource_data) {
                bin.emplace(std::get<2>(data));
            }
        }
    }

    template <HistoryInitialisationMode init_mode = HistoryInitialisationMode::Error>
    void set_values(std::initializer_list<std::pair<ResourceIdT, std::string>> resources)
    {
        set_values<init_mode, std::initializer_list<std::pair<ResourceIdT, std::string>>>(resources);
    }
};

// The root history manager class.
class HistoryManager {
private:
    // Shared state.
    std::shared_ptr<detail::HistoryManagerPrivate> _h;

public:
    AMULET_CORE_EXPORT HistoryManager();

    // The public mutex.
    // Note the mutex is shared with the HistoryManagerLayer class.
    // Thread safe.
    AMULET_CORE_EXPORT std::shared_mutex& get_mutex();

    // Get a new history layer.
    // Unique lock required.
    template <ResourceId ResourceIdT>
    std::shared_ptr<HistoryManagerLayer<ResourceIdT>> new_layer()
    {
        auto& layer_id = _h->layer_count;
        if (std::numeric_limits<LayerId>::max() < layer_id) {
            throw std::runtime_error("Exceeded the maximum number of layers (2^16)");
        }
        auto layer = std::shared_ptr<HistoryManagerLayer<ResourceIdT>>(
            new HistoryManagerLayer<ResourceIdT>(_h, static_cast<LayerId>(layer_id)));
        _h->layers.push_back(layer);
        layer_id++;
        return layer;
    }

    // Reset all history data.
    // Unique lock required.
    AMULET_CORE_EXPORT void reset();

    // Mark the current state as the saved state.
    // Unique lock required.
    AMULET_CORE_EXPORT void mark_saved();

    // Create a new undo bin that new changes will be put in.
    // Unique lock required.
    AMULET_CORE_EXPORT void create_undo_bin();

    // Get the number of times undo can be called.
    // Shared or unique lock required.
    AMULET_CORE_EXPORT size_t get_undo_count();

    // Undo the changes made in the current bin.
    // Unique lock required.
    AMULET_CORE_EXPORT void undo();

    // Get the number of times redo can be called.
    // Shared or unique lock required.
    AMULET_CORE_EXPORT size_t get_redo_count();

    // Redo the changes in the next bin.
    // Unique lock required.
    AMULET_CORE_EXPORT void redo();
};

} // namespace Amulet
