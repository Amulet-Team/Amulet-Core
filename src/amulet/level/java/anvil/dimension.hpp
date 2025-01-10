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
#include <utility>

#include <amulet_nbt/tag/named_tag.hpp>

#include "region.hpp"
#include <amulet/dll.hpp>

namespace Amulet {

class AnvilRegionCoordIterator {
private:
    std::filesystem::directory_iterator it;
    std::pair<std::int64_t, std::int64_t> coord;

    void seek_to_valid();
    void seek_to_next_valid();

public:
    using difference_type = std::ptrdiff_t;
    using value_type = std::pair<std::int64_t, std::int64_t>;

    AMULET_CORE_DLLX AnvilRegionCoordIterator();
    AMULET_CORE_DLLX AnvilRegionCoordIterator(const std::filesystem::path&);
    AMULET_CORE_DLLX std::pair<std::int64_t, std::int64_t> operator*() const;
    AMULET_CORE_DLLX AnvilRegionCoordIterator& operator++();
    AMULET_CORE_DLLX AnvilRegionCoordIterator operator++(int);
    AMULET_CORE_DLLX bool operator==(const AnvilRegionCoordIterator&);
};

static_assert(std::input_iterator<AnvilRegionCoordIterator>);

class AnvilChunkCoordIterator {
private:
    std::weak_ptr<class AnvilDimensionLayer> layer;
    AnvilRegionCoordIterator region_it;
    using coordsT = std::vector<std::pair<std::int64_t, std::int64_t>>;
    coordsT coords;
    coordsT::iterator coord_it;

    void seek_to_valid();
    void seek_to_next_valid();

public:
    using difference_type = std::ptrdiff_t;
    using value_type = std::pair<std::int64_t, std::int64_t>;

    AMULET_CORE_DLLX AnvilChunkCoordIterator();
    AMULET_CORE_DLLX AnvilChunkCoordIterator(std::weak_ptr<class AnvilDimensionLayer>, const std::filesystem::path&);
    AMULET_CORE_DLLX std::pair<std::int64_t, std::int64_t> operator*() const;
    AMULET_CORE_DLLX AnvilChunkCoordIterator& operator++();
    AMULET_CORE_DLLX AnvilChunkCoordIterator operator++(int);
    AMULET_CORE_DLLX bool operator==(const AnvilChunkCoordIterator&);
};

static_assert(std::input_iterator<AnvilChunkCoordIterator>);

// In the Anvil format chunk data is split into layers.
// Historically there was only one layer but entity data was split into its own layer.

class AnvilDimensionLayer {
private:
    std::mutex _mutex;
    std::filesystem::path _directory;
    bool _mcc;
    std::map<std::pair<std::int64_t, std::int64_t>, std::shared_ptr<Amulet::AnvilRegion>> _regions;

public:
    AMULET_CORE_DLLX AnvilDimensionLayer(std::filesystem::path directory, bool mcc = false);
    // Region
    // Get the path to the region file
    std::filesystem::path region_path(std::int64_t rx, std::int64_t rz) const;
    // An iterator of all region coordinates in this layer.
    AMULET_CORE_DLLX AnvilRegionCoordIterator all_region_coords();
    // Check if a region file exists in this layer.
    bool has_region(std::int64_t rx, std::int64_t rz) const;
    // Get an AnvilRegion instance. This must not be stored long-term.
    std::shared_ptr<AnvilRegion> get_region(std::int64_t rx, std::int64_t rz, bool create = false);

    // Chunk
    AMULET_CORE_DLLX AnvilChunkCoordIterator all_chunk_coords();
    // Check if the chunk has data in this layer.
    AMULET_CORE_DLLX bool has_chunk(std::int64_t cx, std::int64_t cz);
    // Get the chunk data for this layer.
    AMULET_CORE_DLLX AmuletNBT::NamedTag get_chunk_data(std::int64_t cx, std::int64_t cz);
    // Set the chunk data for this layer.
    AMULET_CORE_DLLX void set_chunk_data(std::int64_t cx, std::int64_t cz, const AmuletNBT::NamedTag&);
    // Delete the chunk data from this layer.
    AMULET_CORE_DLLX void delete_chunk(std::int64_t cx, std::int64_t cz);
    // Defragment the region files and remove unused region files.
    AMULET_CORE_DLLX void compact();
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
    AnvilDimension(std::filesystem::path directory, bool mcc = false, layersT layer_names)
        : _directory(directory)
        , _mcc(mcc)
    {
        if (layer_names.empty()) {
            throw std::invalid_argument("layer_names must contain at least one name.");
        }
        for (const auto& layer_name : layer_names) {
            _layers.emplace(layer_name, std::make_shared<AnvilDimensionLayer>(_directory / layer_name, _mcc));
        }
        _default_layer = _layers[*layer_names.begin()];
    }

    // Check if this dimension has the requested layer.
    AMULET_CORE_DLLX bool has_layer(const std::string& name);
    // Get the AnvilDimensionLayer for a specific layer. The returned value must not be stored long-term.
    AMULET_CORE_DLLX std::shared_ptr<AnvilDimensionLayer> get_layer(const std::string& name);

    // Get an iterator for all the chunks that exist.
    AMULET_CORE_DLLX AnvilChunkCoordIterator all_chunk_coords() const;
    // Check if a chunk exists.
    AMULET_CORE_DLLX bool has_chunk(std::int64_t cx, std::int64_t cz) const;
    // Get the data for a chunk
    AMULET_CORE_DLLX std::map<std::string, AmuletNBT::NamedTag> get_chunk_data(std::int64_t cx, std::int64_t cz);
    // Set the data for a chunk. If the value is nullopt it will be deleted.
    AMULET_CORE_DLLX void set_chunk_data(std::int64_t cx, std::int64_t cz, const std::map<std::string, std::optional<AmuletNBT::NamedTag>>&);
    // Delete all data for the given chunk.
    AMULET_CORE_DLLX void delete_chunk(std::int64_t cx, std::int64_t cz);
    // Defragment the region files and remove unused region files.
    AMULET_CORE_DLLX void compact();
};

} // namespace Amulet
