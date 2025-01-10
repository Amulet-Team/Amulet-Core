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
AMULET_CORE_DLLX std::pair<std::int64_t, std::int64_t> AnvilRegionCoordIterator::operator*() const
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
AMULET_CORE_DLLX bool AnvilRegionCoordIterator::operator==(const AnvilRegionCoordIterator& other)
{
    return it == other.it;
}

// AnvilChunkCoordIterator
void AnvilChunkCoordIterator::seek_to_valid();
void AnvilChunkCoordIterator::seek_to_next_valid();
AMULET_CORE_DLLX AnvilChunkCoordIterator::AnvilChunkCoordIterator() { }
AMULET_CORE_DLLX AnvilChunkCoordIterator::AnvilChunkCoordIterator(const std::filesystem::path&);
AMULET_CORE_DLLX std::pair<std::int64_t, std::int64_t> AnvilChunkCoordIterator::operator*() const;
AMULET_CORE_DLLX AnvilChunkCoordIterator& AnvilChunkCoordIterator::operator++();
AMULET_CORE_DLLX AnvilChunkCoordIterator AnvilChunkCoordIterator::operator++(int);
AMULET_CORE_DLLX bool AnvilChunkCoordIterator::operator==(const AnvilChunkCoordIterator&);

// AnvilDimensionLayer
AMULET_CORE_DLLX AnvilDimensionLayer::AnvilDimensionLayer(
    std::filesystem::path directory, bool mcc = false)
    : _directory(directory)
    , _mcc(mcc)
{
    if (!std::filesystem::is_directory(_directory)) {
        throw std::invalid_argument("path is not a directory");
    }
}
std::filesystem::path AnvilDimensionLayer::region_path(
    std::int64_t rx, std::int64_t rz) const
{
    return _directory / ("r." + std::to_string(rx) + "." + std::to_string(rz) + ".mca");
}
bool AnvilDimensionLayer::has_region(
    std::int64_t rx, std::int64_t rz) const
{
    return std::filesystem::is_regular_file(region_path(rx, rz));
}
std::shared_ptr<AnvilRegion> AnvilDimensionLayer::get_region(
    std::int64_t rx, std::int64_t rz, bool create = false)
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
        auto emp = _regions.try_emplace(key, _directory, rx, rz, _mcc);
        return emp.first->second;
    } else {
        throw ChunkDoesNotExist();
    }
}

AnvilRegionCoordIterator AnvilDimensionLayer::all_region_coords()
{
    return AnvilRegionCoordIterator(_directory);
}
AMULET_CORE_DLLX AnvilChunkCoordIterator AnvilDimensionLayer::all_chunk_coords()
{
}
AMULET_CORE_DLLX bool AnvilDimensionLayer::has_chunk(std::int64_t cx, std::int64_t cz)
{
    try {
        return get_region(cx >> 5, cz >> 5)->has_value(cx, cz);
    } catch (Amulet::ChunkDoesNotExist) {
        return false;
    }
}
AMULET_CORE_DLLX AmuletNBT::NamedTag AnvilDimensionLayer::get_chunk_data(std::int64_t cx, std::int64_t cz)
{
    return get_region(cx >> 5, cz >> 5)->get_value(cx, cz);
}
AMULET_CORE_DLLX void AnvilDimensionLayer::set_chunk_data(std::int64_t cx, std::int64_t cz, const AmuletNBT::NamedTag& tag)
{
    return get_region(cx >> 5, cz >> 5, true)->set_value(cx, cz, tag);
}
AMULET_CORE_DLLX void AnvilDimensionLayer::delete_chunk(std::int64_t cx, std::int64_t cz)
{
    try {
        get_region(cx >> 5, cz >> 5)->delete_value(cx, cz);
    } catch (Amulet::ChunkDoesNotExist) {
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

AMULET_CORE_DLLX bool AnvilDimension::has_layer(const std::string& name)
{
    std::shared_lock lock(_mutex);
    return _layers.contains(name);
}
AMULET_CORE_DLLX std::shared_ptr<AnvilDimensionLayer> AnvilDimension::get_layer(const std::string& name)
{
    std::shared_lock lock(_mutex);
    auto it = _layers.find(name);
    if (it == _layers.end()) {
        throw std::invalid_argument("No layer exists with name " + name);
    }
    return it->second;
}

AMULET_CORE_DLLX AnvilChunkCoordIterator AnvilDimension::all_chunk_coords() const
{
    return _default_layer->all_chunk_coords();
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
            chunk_data[layer_name] = layer->get_chunk_data(cx, cz);
        } catch (ChunkDoesNotExist) {
        }
    }
    if (chunk_data.empty()) {
        throw ChunkDoesNotExist();
    }
    return chunk_data;
}
AMULET_CORE_DLLX void AnvilDimension::set_chunk_data(std::int64_t cx, std::int64_t cz, const std::map<std::string, std::optional<AmuletNBT::NamedTag>>& data_layers)
{
    std::shared_lock slock(_mutex);
    for (const auto& [layer_name, data] : data_layers) {
        auto it = _layers.find(layer_name);
        if (it == _layers.end()) {
            // Layer does not currently exist.
            if (!data) {
                // If it was going to be deleted then do nothing.
                continue;
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
        if (data) {
            it->second->set_chunk_data(cx, cz, *data);
        } else {
            it->second->delete_chunk(cx, cz);
        }
    }
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

} // namespace Amulet
