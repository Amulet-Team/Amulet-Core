#pragma once

#include <cstdint>
#include <filesystem>
#include <iterator>
#include <map>
#include <memory>
#include <mutex>
#include <optional>
#include <ranges>
#include <shared_mutex>
#include <string>
#include <type_traits>
#include <utility>

#include <amulet_nbt/tag/named_tag.hpp>

#include "region.hpp"
#include <amulet/dll.hpp>
#include <amulet/utils/mutex.hpp>
#include <amulet/utils/logging.hpp>

namespace Amulet {

template <bool condition, typename... values>
struct Ensure {
    static_assert(condition);
    static bool const value = condition;
};

// An input iterator over region coordinates in a directory.
class AnvilRegionCoordIterator {
    // Not thread safe.
private:
    std::filesystem::directory_iterator it;
    std::pair<std::int64_t, std::int64_t> coord;

    void seek_to_valid();
    void seek_to_next_valid();

public:
    using difference_type = std::ptrdiff_t;
    using value_type = std::pair<std::int64_t, std::int64_t>;

    AMULET_CORE_EXPORT AnvilRegionCoordIterator();
    AMULET_CORE_EXPORT AnvilRegionCoordIterator(const std::filesystem::path&);
    AMULET_CORE_EXPORT const std::pair<std::int64_t, std::int64_t>& operator*() const;
    AMULET_CORE_EXPORT AnvilRegionCoordIterator& operator++();
    AMULET_CORE_EXPORT void operator++(int);
    friend AMULET_CORE_EXPORT bool operator==(const AnvilRegionCoordIterator&, const AnvilRegionCoordIterator&);
};

AMULET_CORE_EXPORT bool operator==(const AnvilRegionCoordIterator&, const AnvilRegionCoordIterator&);

static_assert(std::input_iterator<AnvilRegionCoordIterator>);

// An input iterator over chunk coordinates in a dimension layer.
// Layer's Read::SharedReadWrite lock required.
// Layer's Read::SharedReadOnly lock optional.
class AnvilChunkCoordIterator {
    // Not thread safe.
private:
    std::weak_ptr<class AnvilDimensionLayer> _layer;
    AnvilRegionCoordIterator _region_it;
    using coordsT = std::vector<std::pair<std::int64_t, std::int64_t>>;
    coordsT _coords;
    coordsT::iterator _coord_it;

    void seek_to_valid();
    void seek_to_next_valid();

public:
    using difference_type = std::ptrdiff_t;
    using value_type = std::pair<std::int64_t, std::int64_t>;

    AMULET_CORE_EXPORT AnvilChunkCoordIterator();
    AMULET_CORE_EXPORT AnvilChunkCoordIterator(std::shared_ptr<class AnvilDimensionLayer>);
    AMULET_CORE_EXPORT std::pair<std::int64_t, std::int64_t> operator*() const;
    AMULET_CORE_EXPORT AnvilChunkCoordIterator& operator++();
    AMULET_CORE_EXPORT void operator++(int);
    friend AMULET_CORE_EXPORT bool operator==(const AnvilChunkCoordIterator&, const AnvilChunkCoordIterator&);
};

AMULET_CORE_EXPORT bool operator==(const AnvilChunkCoordIterator&, const AnvilChunkCoordIterator&);

static_assert(std::input_iterator<AnvilChunkCoordIterator>);

// In the Anvil format chunk data is split into layers.
// Historically there was only one layer but entity data was split into its own layer.

// A class to manage a directory of region files.
class AnvilDimensionLayer {
private:
    Amulet::OrderedMutex _public_mutex;
    std::filesystem::path _directory;
    bool _mcc;
    std::mutex _regions_mutex;
    std::map<std::pair<std::int64_t, std::int64_t>, std::shared_ptr<Amulet::AnvilRegion>> _regions;
    bool destroyed = false;

public:
    // Constructors
    AnvilDimensionLayer() = delete;
    AnvilDimensionLayer(const AnvilDimensionLayer&) = delete;
    AnvilDimensionLayer(AnvilDimensionLayer&&) = delete;
    AMULET_CORE_EXPORT AnvilDimensionLayer(std::filesystem::path directory, bool mcc = false);

    // Destructor
    AMULET_CORE_EXPORT ~AnvilDimensionLayer();

    // Accessors

    // External mutex.
    // Thread safe.
    AMULET_CORE_EXPORT Amulet::OrderedMutex& get_mutex();

    // The directory this instance manages.
    // Thread safe.
    AMULET_CORE_EXPORT const std::filesystem::path& directory() const;

    // Is mcc file support enabled for this instance.
    // Thread safe.
    AMULET_CORE_EXPORT bool mcc() const;

    // Region

    // Get the path to the region file
    // Thread safe.
    std::filesystem::path region_path(std::int64_t rx, std::int64_t rz) const;

    // An iterator of all region coordinates in this layer.
    // External Read::SharedReadWrite lock required.
    // External Read::SharedReadOnly lock optional.
    AMULET_CORE_EXPORT AnvilRegionCoordIterator all_region_coords();

    // Check if a region file exists in this layer at given the coordinates.
    // External Read::SharedReadWrite lock required.
    // External Read::SharedReadOnly lock optional.
    AMULET_CORE_EXPORT bool has_region(std::int64_t rx, std::int64_t rz) const;

    // Check if a region file exists in this layer that contains the given chunk.
    // External Read::SharedReadWrite lock required.
    // External Read::SharedReadOnly lock optional.
    AMULET_CORE_EXPORT bool has_region_at_chunk(std::int64_t cx, std::int64_t cz) const;

    // Get an AnvilRegion instance from its coordinates. This must not be stored long-term.
    // Will throw RegionDoesNotExist if create is false and the region does not exist.
    // External Read::SharedReadWrite lock required if only calling Read methods on AnvilRegion.
    // External ReadWrite::SharedReadWrite lock required if calling ReadWrite methods on AnvilRegion.
    AMULET_CORE_EXPORT std::shared_ptr<AnvilRegion> get_region(std::int64_t rx, std::int64_t rz, bool create = false);

    // Get an AnvilRegion instance from chunk coordinates it contains. This must not be stored long-term.
    // Will throw RegionDoesNotExist if create is false and the region does not exist.
    // External Read::SharedReadWrite lock required if only calling Read methods on AnvilRegion.
    // External ReadWrite::SharedReadWrite lock required if calling ReadWrite methods on AnvilRegion.
    AMULET_CORE_EXPORT std::shared_ptr<AnvilRegion> get_region_at_chunk(std::int64_t cx, std::int64_t cz, bool create = false);

    // Chunk

    // Check if the chunk has data in this layer.
    // External Read::SharedReadWrite lock required.
    // External Read::SharedReadOnly lock optional.
    AMULET_CORE_EXPORT bool has_chunk(std::int64_t cx, std::int64_t cz);

    // Get the chunk data for this layer.
    // Will throw ChunkDoesNotExist if the chunk does not exist.
    // External Read::SharedReadWrite lock required.
    AMULET_CORE_EXPORT AmuletNBT::NamedTag get_chunk_data(std::int64_t cx, std::int64_t cz);

    // Set the chunk data for this layer.
    // External ReadWrite::SharedReadWrite lock required.
    AMULET_CORE_EXPORT void set_chunk_data(std::int64_t cx, std::int64_t cz, const AmuletNBT::NamedTag&);

    // Delete the chunk data from this layer.
    // External ReadWrite::SharedReadWrite lock required.
    AMULET_CORE_EXPORT void delete_chunk(std::int64_t cx, std::int64_t cz);

    // Defragment the region files and remove unused region files.
    // External ReadWrite::SharedReadOnly lock required.
    AMULET_CORE_EXPORT void compact();

    // Destroy the instance.
    // Calls made after this will fail.
    // This may only be called by the owner of the instance.
    // External ReadWrite:Unique lock required.
    AMULET_CORE_EXPORT void destroy();

    // Has the instance been destroyed.
    // If this is false, other calls will fail.
    // External Read:SharedReadWrite lock required.
    AMULET_CORE_EXPORT bool is_destroyed();
};

template <typename Range, typename T>
concept TypedInputRange = std::ranges::input_range<Range> && std::convertible_to<std::ranges::range_value_t<Range>, T>;

using JavaRawChunk = std::map<std::string, AmuletNBT::NamedTag>;

class AnvilDimension {
private:
    Amulet::OrderedMutex _public_mutex;
    std::filesystem::path _directory;
    bool _mcc;
    std::shared_mutex _layers_mutex;
    std::map<std::string, std::shared_ptr<AnvilDimensionLayer>> _layers;
    std::shared_ptr<AnvilDimensionLayer> _default_layer;
    bool destroyed = false;

public:
    template <TypedInputRange<std::string> layersT>
    AnvilDimension(std::filesystem::path directory, layersT layer_names, bool mcc = false)
        : _directory(directory)
        , _mcc(mcc)
    {
        if (layer_names.begin() == layer_names.end()) {
            throw std::invalid_argument("layer_names must contain at least one name.");
        }
        for (const auto& layer_name : layer_names) {
            _layers.emplace(layer_name, std::make_shared<AnvilDimensionLayer>(_directory / layer_name, _mcc));
        }
        _default_layer = _layers[*layer_names.begin()];
    }

    // Destructor
    AMULET_CORE_EXPORT ~AnvilDimension();

    // External mutex.
    // Thread safe.
    AMULET_CORE_EXPORT Amulet::OrderedMutex& get_mutex();

    // The directory this dimension is in.
    // Thread safe.
    AMULET_CORE_EXPORT const std::filesystem::path& directory() const;

    // Are mcc files enabled for this dimension.
    // Thread safe.
    AMULET_CORE_EXPORT bool mcc() const;

    // Get the names of all layers in this dimension.
    // External Read::SharedReadWrite lock required.
    // External Read::SharedReadOnly lock optional.
    AMULET_CORE_EXPORT std::vector<std::string> layer_names();

    // Check if this dimension has the requested layer.
    // External Read::SharedReadWrite lock required.
    // External Read::SharedReadOnly lock optional.
    AMULET_CORE_EXPORT bool has_layer(const std::string& layer_name);

    // Get the AnvilDimensionLayer for a specific layer. The returned value must not be stored long-term.
    // If create=true the layer will be created if it doesn't exist.
    // External Read::SharedReadWrite lock required if only calling Read methods on AnvilDimensionLayer.
    // External ReadWrite::SharedReadWrite lock required if create=true or calling ReadWrite methods on AnvilDimensionLayer.
    AMULET_CORE_EXPORT std::shared_ptr<AnvilDimensionLayer> get_layer(const std::string& layer_name, bool create = false);

    // Get an iterator for all the chunks that exist in this dimension.
    // External Read::SharedReadWrite lock required.
    // External Read::SharedReadOnly lock optional.
    AMULET_CORE_EXPORT AnvilChunkCoordIterator all_chunk_coords() const;

    // Check if a chunk exists.
    // External Read::SharedReadWrite lock required.
    // External Read::SharedReadOnly lock optional.
    AMULET_CORE_EXPORT bool has_chunk(std::int64_t cx, std::int64_t cz) const;

    // Get the data for a chunk
    // External Read::SharedReadWrite lock required.
    AMULET_CORE_EXPORT JavaRawChunk get_chunk_data(std::int64_t cx, std::int64_t cz);

    // Set the data for a chunk.
    // data_layers can be any object supporting std::ranges::input_range of [std::string, AmuletNBT::NamedTag || std::optional<AmuletNBT::NamedTag>]
    // If the second value is a nullopt optional, the value will be deleted.
    // External ReadWrite::SharedReadWrite lock required.
    template <typename dataT>
    void set_chunk_data(std::int64_t cx, std::int64_t cz, const dataT& data_layers)
    {
        std::shared_lock slock(_layers_mutex);
        for (const auto& [layer_name, data] : data_layers) {
            static_assert(Ensure<
                std::is_same_v<decltype(layer_name), const std::string>,
                decltype(layer_name),
                const std::string>::value);
            static_assert(Ensure < std::is_same_v<decltype(data), const AmuletNBT::NamedTag> || std::is_same_v<decltype(data), const std::optional<AmuletNBT::NamedTag>>,
                decltype(layer_name),
                const AmuletNBT::NamedTag,
                const std::optional < AmuletNBT::NamedTag >> ::value);
            std::map<std::string, std::shared_ptr<AnvilDimensionLayer>>::iterator it = _layers.find(layer_name);
            if (it == _layers.end()) {
                // Layer does not currently exist.
                if constexpr (std::is_same_v<decltype(data), const std::optional<AmuletNBT::NamedTag>>) {
                    if (!data) {
                        // If it was going to be deleted then do nothing.
                        continue;
                    }
                } else if (std::all_of(layer_name.begin(), layer_name.end(), [](char c) { return 0x61 <= c && c <= 0x7A; })) {
                    if (destroyed) {
                        throw std::runtime_error("This AnvilDimension instance has been destroyed.");
                    }
                    // Switch to a unique lock to mutate _layers
                    slock.unlock();
                    std::unique_lock ulock(_layers_mutex);
                    // Create the layer.
                    it = _layers.emplace(layer_name, std::make_shared<AnvilDimensionLayer>(_directory / layer_name, _mcc)).first;
                    // Switch back to a shared lock
                    ulock.unlock();
                    slock.lock();
                } else {
                    error("Anvil layer contains characters not in the range a-z");
                    continue;
                }
            }
            auto& layer = it->second;
            auto& layer_mutex = layer->get_mutex();
            layer_mutex.lock<ThreadAccessMode::ReadWrite, ThreadShareMode::SharedReadWrite>();
            std::lock_guard lock(layer_mutex, std::adopt_lock);
            if constexpr (std::is_same_v<decltype(data), const std::optional<AmuletNBT::NamedTag>>) {
                if (data) {
                    layer->set_chunk_data(cx, cz, *data);
                } else {
                    layer->delete_chunk(cx, cz);
                }
            } else {
                layer->set_chunk_data(cx, cz, data);
            }
        }
    }

    // Delete all data for the given chunk.
    // External ReadWrite::SharedReadWrite lock required.
    AMULET_CORE_EXPORT void delete_chunk(std::int64_t cx, std::int64_t cz);

    // Defragment the region files and remove unused region files.
    // External ReadWrite::SharedReadOnly lock required.
    AMULET_CORE_EXPORT void compact();

    // Destroy the instance.
    // Calls made after this will fail.
    // This may only be called by the owner of the instance.
    // External ReadWrite:Unique lock required.
    AMULET_CORE_EXPORT void destroy();

    // Has the instance been destroyed.
    // If this is false, other calls will fail.
    // External Read:SharedReadWrite lock required.
    AMULET_CORE_EXPORT bool is_destroyed();
};

} // namespace Amulet
