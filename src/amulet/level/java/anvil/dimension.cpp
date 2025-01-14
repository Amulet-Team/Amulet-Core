#include <algorithm>

#include <amulet/chunk.hpp>

#include "dimension.hpp"
#include "region.hpp"

namespace Amulet {

// AnvilRegionCoordIterator
void AnvilRegionCoordIterator::seek_to_valid()
{
    for (; it != std::filesystem::directory_iterator(); it++) {
        try {
            if (!it->is_regular_file()) {
                continue;
            }
            coord = parse_region_filename(it->path().filename().string());
            return;
        } catch (std::invalid_argument) {
            continue;
        }
    }
}

void AnvilRegionCoordIterator::seek_to_next_valid()
{
    if (it != std::filesystem::directory_iterator()) {
        it++;
        seek_to_valid();
    }
}

AMULET_CORE_DLLX AnvilRegionCoordIterator::AnvilRegionCoordIterator() { }
AMULET_CORE_DLLX AnvilRegionCoordIterator::AnvilRegionCoordIterator(const std::filesystem::path& path)
    : it(path)
{
    // Seek to first valid region
    seek_to_valid();
}
AMULET_CORE_DLLX const std::pair<std::int64_t, std::int64_t>& AnvilRegionCoordIterator::operator*() const
{
    return coord;
}
AMULET_CORE_DLLX AnvilRegionCoordIterator& AnvilRegionCoordIterator::operator++()
{
    seek_to_next_valid();
    return *this;
}
AMULET_CORE_DLLX AnvilRegionCoordIterator AnvilRegionCoordIterator::operator++(int)
{
    auto rv = *this;
    seek_to_next_valid();
    return rv;
}
AMULET_CORE_DLLX bool operator==(const AnvilRegionCoordIterator& lhs, const AnvilRegionCoordIterator& rhs)
{
    return lhs.it == rhs.it;
}

// AnvilChunkCoordIterator
void AnvilChunkCoordIterator::seek_to_valid()
{
    auto layer = _layer.lock();
    if (!layer) {
        throw std::runtime_error("layer attached to AnvilChunkCoordIterator has been destroyed.");
    }
    for (; _region_it != AnvilRegionCoordIterator(); _region_it++) {
        const auto& [rx, rz] = *_region_it;
        std::shared_ptr<AnvilRegion> region;
        try {
            region = layer->get_region(rx, rz);
        } catch (RegionDoesNotExist) {
            continue;
        }
        _coords = region->get_coords();
        _coord_it = _coords.begin();
        if (!_coords.empty()) {
            return;
        }
    }
}
void AnvilChunkCoordIterator::seek_to_next_valid()
{
    if (_coord_it != _coords.end()) {
        _coord_it++;
    }
    if (_coord_it == _coords.end()) {
        seek_to_valid();
    }
}
AMULET_CORE_DLLX AnvilChunkCoordIterator::AnvilChunkCoordIterator() { }
AMULET_CORE_DLLX AnvilChunkCoordIterator::AnvilChunkCoordIterator(std::shared_ptr<class AnvilDimensionLayer> layer)
    : _layer(std::move(layer))
    , _region_it(layer->all_region_coords())
    , _coord_it(_coords.end())
{
    seek_to_valid();
}
AMULET_CORE_DLLX std::pair<std::int64_t, std::int64_t> AnvilChunkCoordIterator::operator*() const
{
    return *_coord_it;
}
AMULET_CORE_DLLX AnvilChunkCoordIterator& AnvilChunkCoordIterator::operator++()
{
    seek_to_next_valid();
    return *this;
}
AMULET_CORE_DLLX AnvilChunkCoordIterator AnvilChunkCoordIterator::operator++(int)
{
    auto rv = *this;
    seek_to_next_valid();
    return rv;
}
AMULET_CORE_DLLX bool operator==(const AnvilChunkCoordIterator& lhs, const AnvilChunkCoordIterator& rhs)
{
    return lhs._region_it == AnvilRegionCoordIterator() && rhs._region_it == AnvilRegionCoordIterator();
}

// AnvilDimensionLayer
AMULET_CORE_DLLX AnvilDimensionLayer::AnvilDimensionLayer(
    std::filesystem::path directory, bool mcc)
    : _directory(directory)
    , _mcc(mcc)
{
    if (!std::filesystem::is_directory(_directory)) {
        throw std::invalid_argument("path is not a directory");
    }
}

// Accessors
AMULET_CORE_DLLX const std::filesystem::path& AnvilDimensionLayer::directory() const { return _directory; }
AMULET_CORE_DLLX bool AnvilDimensionLayer::mcc() const { return _mcc; }

std::filesystem::path AnvilDimensionLayer::region_path(
    std::int64_t rx, std::int64_t rz) const
{
    return _directory / ("r." + std::to_string(rx) + "." + std::to_string(rz) + ".mca");
}
AMULET_CORE_DLLX bool AnvilDimensionLayer::has_region(
    std::int64_t rx, std::int64_t rz) const
{
    return std::filesystem::is_regular_file(region_path(rx, rz));
}
AMULET_CORE_DLLX std::shared_ptr<AnvilRegion> AnvilDimensionLayer::get_region(
    std::int64_t rx, std::int64_t rz, bool create)
{
    // Lock parallel modifications
    std::lock_guard<std::mutex> guard(_mutex);
    // Get the region key
    auto key = std::make_pair(rx, rz);
    // Find the region
    auto it = _regions.find(key);
    if (it != _regions.end()) {
        // Return if it already exists.
        return it->second;
    } else if (create or has_region(rx, rz)) {
        // Create the region class
        auto emp = _regions.emplace(key, std::make_shared<AnvilRegion>(_directory, rx, rz, _mcc));
        return emp.first->second;
    } else {
        throw RegionDoesNotExist();
    }
}

AnvilRegionCoordIterator AnvilDimensionLayer::all_region_coords()
{
    return AnvilRegionCoordIterator(_directory);
}
AMULET_CORE_DLLX bool AnvilDimensionLayer::has_chunk(std::int64_t cx, std::int64_t cz)
{
    try {
        return get_region(cx >> 5, cz >> 5)->has_value(cx, cz);
    } catch (RegionDoesNotExist) {
        return false;
    }
}
AMULET_CORE_DLLX AmuletNBT::NamedTag AnvilDimensionLayer::get_chunk_data(std::int64_t cx, std::int64_t cz)
{
    try {
        return get_region(cx >> 5, cz >> 5)->get_value(cx, cz);
    } catch (RegionDoesNotExist) {
        throw ChunkDoesNotExist("Chunk " + std::to_string(cx) + ", " + std::to_string(cz) + "does not exist.");
    }
}
AMULET_CORE_DLLX void AnvilDimensionLayer::set_chunk_data(std::int64_t cx, std::int64_t cz, const AmuletNBT::NamedTag& tag)
{
    return get_region(cx >> 5, cz >> 5, true)->set_value(cx, cz, tag);
}
AMULET_CORE_DLLX void AnvilDimensionLayer::delete_chunk(std::int64_t cx, std::int64_t cz)
{
    try {
        get_region(cx >> 5, cz >> 5)->delete_value(cx, cz);
    } catch (RegionDoesNotExist) {
        return;
    }
}
AMULET_CORE_DLLX void AnvilDimensionLayer::compact()
{
    for (auto it = all_region_coords(); it != AnvilRegionCoordIterator(); it++) {
        auto [cx, cz] = *it;
        auto region = get_region(cx, cz);
        region->compact();
    }
}

AMULET_CORE_DLLX bool AnvilDimension::has_layer(const std::string& layer_name)
{
    std::shared_lock lock(_mutex);
    return _layers.contains(layer_name);
}
AMULET_CORE_DLLX std::shared_ptr<AnvilDimensionLayer> AnvilDimension::get_layer(const std::string& layer_name)
{
    std::shared_lock lock(_mutex);
    auto it = _layers.find(layer_name);
    if (it == _layers.end()) {
        throw std::invalid_argument("No layer exists with name " + layer_name);
    }
    return it->second;
}

AMULET_CORE_DLLX AnvilChunkCoordIterator AnvilDimension::all_chunk_coords() const
{
    return AnvilChunkCoordIterator(_default_layer);
}
AMULET_CORE_DLLX bool AnvilDimension::has_chunk(std::int64_t cx, std::int64_t cz) const
{
    return _default_layer->has_chunk(cx, cz);
}
AMULET_CORE_DLLX std::map<std::string, AmuletNBT::NamedTag> AnvilDimension::get_chunk_data(std::int64_t cx, std::int64_t cz)
{
    std::shared_lock lock(_mutex);
    std::map<std::string, AmuletNBT::NamedTag> chunk_data;
    for (const auto& [layer_name, layer] : _layers) {
        try {
            chunk_data.emplace(layer_name, layer->get_chunk_data(cx, cz));
        } catch (ChunkDoesNotExist) {
        }
    }
    if (chunk_data.empty()) {
        throw ChunkDoesNotExist();
    }
    return chunk_data;
}
AMULET_CORE_DLLX void AnvilDimension::delete_chunk(std::int64_t cx, std::int64_t cz)
{
    for (const auto& layer : _layers) {
        layer.second->delete_chunk(cx, cz);
    }
}
AMULET_CORE_DLLX void AnvilDimension::compact()
{
    for (const auto& layer : _layers) {
        layer.second->compact();
    }
}

} // namespace Amulet
