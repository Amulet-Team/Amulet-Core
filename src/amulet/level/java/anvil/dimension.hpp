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

namespace Amulet {

template <bool condition, typename... values>
struct Ensure {
    static_assert(condition);
    static bool const value = condition;
};

class AnvilRegionCoordIterator {
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

class AnvilChunkCoordIterator {
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

class AnvilDimensionLayer {
private:
    std::mutex _mutex;
    std::shared_mutex _public_mutex;
    std::filesystem::path _directory;
    bool _mcc;
    std::map<std::pair<std::int64_t, std::int64_t>, std::shared_ptr<Amulet::AnvilRegion>> _regions;

public:
    // Accessors

    // External mutex.
    // This must be acquired in unique mode before mutating the layer.
    // This may be acquired in shared (or unique) mode before reading the layer.
    AMULET_CORE_EXPORT std::shared_mutex& mutex();

    AMULET_CORE_EXPORT const std::filesystem::path& directory() const;
    AMULET_CORE_EXPORT bool mcc() const;

    AMULET_CORE_EXPORT AnvilDimensionLayer(std::filesystem::path directory, bool mcc = false);
    // Region
    // Get the path to the region file
    std::filesystem::path region_path(std::int64_t rx, std::int64_t rz) const;
    // An iterator of all region coordinates in this layer.
    AMULET_CORE_EXPORT AnvilRegionCoordIterator all_region_coords();
    // Check if a region file exists in this layer.
    AMULET_CORE_EXPORT bool has_region(std::int64_t rx, std::int64_t rz) const;
    // Get an AnvilRegion instance. This must not be stored long-term.
    AMULET_CORE_EXPORT std::shared_ptr<AnvilRegion> get_region(std::int64_t rx, std::int64_t rz, bool create = false);

    // Chunk
    // Check if the chunk has data in this layer.
    AMULET_CORE_EXPORT bool has_chunk(std::int64_t cx, std::int64_t cz);
    // Get the chunk data for this layer.
    AMULET_CORE_EXPORT AmuletNBT::NamedTag get_chunk_data(std::int64_t cx, std::int64_t cz);
    // Set the chunk data for this layer.
    AMULET_CORE_EXPORT void set_chunk_data(std::int64_t cx, std::int64_t cz, const AmuletNBT::NamedTag&);
    // Delete the chunk data from this layer.
    AMULET_CORE_EXPORT void delete_chunk(std::int64_t cx, std::int64_t cz);
    // Defragment the region files and remove unused region files.
    AMULET_CORE_EXPORT void compact();
};

template <typename Range, typename T>
concept TypedInputRange = std::ranges::input_range<Range> && std::convertible_to<std::ranges::range_value_t<Range>, T>;

class AnvilDimension {
private:
    std::shared_mutex _mutex;
    std::filesystem::path _directory;
    bool _mcc;
    std::map<std::string, std::shared_ptr<AnvilDimensionLayer>> _layers;
    std::shared_ptr<AnvilDimensionLayer> _default_layer;

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

    AMULET_CORE_EXPORT const std::filesystem::path& directory() const;
    AMULET_CORE_EXPORT bool mcc() const;

    // Get the layers defined in this dimension.
    AMULET_CORE_EXPORT std::vector<std::string> layer_names();
    // Check if this dimension has the requested layer.
    AMULET_CORE_EXPORT bool has_layer(const std::string& layer_name);
    // Get the AnvilDimensionLayer for a specific layer. The returned value must not be stored long-term.
    AMULET_CORE_EXPORT std::shared_ptr<AnvilDimensionLayer> get_layer(const std::string& layer_name);

    // Get an iterator for all the chunks that exist in this dimension.
    AMULET_CORE_EXPORT AnvilChunkCoordIterator all_chunk_coords() const;
    // Check if a chunk exists.
    AMULET_CORE_EXPORT bool has_chunk(std::int64_t cx, std::int64_t cz) const;
    // Get the data for a chunk
    AMULET_CORE_EXPORT std::map<std::string, AmuletNBT::NamedTag> get_chunk_data(std::int64_t cx, std::int64_t cz);
    // Set the data for a chunk.
    // data_layers can be any object supporting std::ranges::input_range of [std::string, AmuletNBT::NamedTag || std::optional<AmuletNBT::NamedTag>]
    // If the second value is a nullopt optional, the value will be deleted.
    template <typename dataT>
    void set_chunk_data(std::int64_t cx, std::int64_t cz, const dataT& data_layers)
    {
        std::shared_lock slock(_mutex);
        for (const auto& [layer_name, data] : data_layers) {
            static_assert(Ensure<
                std::is_same_v<decltype(layer_name), const std::string>,
                decltype(layer_name),
                const std::string>::value);
            static_assert(Ensure < std::is_same_v<decltype(data), const AmuletNBT::NamedTag> || std::is_same_v<decltype(data), const std::optional<AmuletNBT::NamedTag>>,
                decltype(layer_name),
                const AmuletNBT::NamedTag,
                const std::optional < AmuletNBT::NamedTag >> ::value);
            auto it = _layers.find(layer_name);
            if (it == _layers.end()) {
                // Layer does not currently exist.
                if constexpr (std::is_same_v<decltype(data), const std::optional<AmuletNBT::NamedTag>>) {
                    if (!data) {
                        // If it was going to be deleted then do nothing.
                        continue;
                    }
                }
                if (std::all_of(layer_name.begin(), layer_name.end(), [](char c) { return 0x61 <= c && c <= 0x7A; })) {
                    // Switch to a unique lock to mutate _layers
                    slock.unlock();
                    std::unique_lock ulock(_mutex);
                    // Create the layer.
                    it = _layers.emplace(layer_name, std::make_shared<AnvilDimensionLayer>(_directory / layer_name, _mcc)).first;
                    // Switch back to a shared lock
                    ulock.unlock();
                    slock.lock();
                }
            }
            if constexpr (std::is_same_v<decltype(data), const std::optional<AmuletNBT::NamedTag>>) {
                if (data) {
                    it->second->set_chunk_data(cx, cz, *data);
                } else {
                    it->second->delete_chunk(cx, cz);
                }
            } else {
                it->second->set_chunk_data(cx, cz, data);
            }
        }
    }
    // Delete all data for the given chunk.
    AMULET_CORE_EXPORT void delete_chunk(std::int64_t cx, std::int64_t cz);
    // Defragment the region files and remove unused region files.
    AMULET_CORE_EXPORT void compact();
};

} // namespace Amulet
