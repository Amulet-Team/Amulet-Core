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

AnvilRegionCoordIterator::AnvilRegionCoordIterator() { }
AnvilRegionCoordIterator::AnvilRegionCoordIterator(const std::filesystem::path& path)
    : it(path)
{
    // Seek to first valid region
    seek_to_valid();
}
const std::pair<std::int64_t, std::int64_t>& AnvilRegionCoordIterator::operator*() const
{
    return coord;
}
AnvilRegionCoordIterator& AnvilRegionCoordIterator::operator++()
{
    seek_to_next_valid();
    return *this;
}
void AnvilRegionCoordIterator::operator++(int)
{
    seek_to_next_valid();
}
bool operator==(const AnvilRegionCoordIterator& lhs, const AnvilRegionCoordIterator& rhs)
{
    return lhs.it == rhs.it;
}

// AnvilChunkCoordIterator
void AnvilChunkCoordIterator::seek_to_valid()
{
    std::shared_ptr<AnvilDimensionLayer> layer;
    for (; _region_it != AnvilRegionCoordIterator(); _region_it++) {
        if (!layer) {
            layer = _layer.lock();
            if (!layer) {
                throw std::runtime_error("layer attached to AnvilChunkCoordIterator has been destroyed.");
            }
        }
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
        if (_region_it == AnvilRegionCoordIterator()) {
            return;
        }
        _region_it++;
        seek_to_valid();
    }
}
AnvilChunkCoordIterator::AnvilChunkCoordIterator() { }
AnvilChunkCoordIterator::AnvilChunkCoordIterator(std::shared_ptr<class AnvilDimensionLayer> layer)
    : _layer(std::move(layer))
    , _region_it(layer->all_region_coords())
    , _coord_it(_coords.end())
{
    seek_to_valid();
}
std::pair<std::int64_t, std::int64_t> AnvilChunkCoordIterator::operator*() const
{
    return *_coord_it;
}
AnvilChunkCoordIterator& AnvilChunkCoordIterator::operator++()
{
    seek_to_next_valid();
    return *this;
}
void AnvilChunkCoordIterator::operator++(int)
{
    seek_to_next_valid();
}
bool operator==(const AnvilChunkCoordIterator& lhs, const AnvilChunkCoordIterator& rhs)
{
    return lhs._region_it == AnvilRegionCoordIterator() && rhs._region_it == AnvilRegionCoordIterator();
}

// AnvilDimensionLayer
AnvilDimensionLayer::AnvilDimensionLayer(
    std::filesystem::path directory, bool mcc)
    : _directory(directory)
    , _mcc(mcc)
{
    if (!std::filesystem::is_directory(_directory)) {
        throw std::invalid_argument("path is not a directory");
    }
}

// Accessors
std::shared_mutex& AnvilDimensionLayer::mutex() { return _public_mutex; }
const std::filesystem::path& AnvilDimensionLayer::directory() const { return _directory; }
bool AnvilDimensionLayer::mcc() const { return _mcc; }

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
bool AnvilDimensionLayer::has_chunk(std::int64_t cx, std::int64_t cz)
{
    try {
        return get_region(cx >> 5, cz >> 5)->has_value(cx, cz);
    } catch (RegionDoesNotExist) {
        return false;
    }
}
AmuletNBT::NamedTag AnvilDimensionLayer::get_chunk_data(std::int64_t cx, std::int64_t cz)
{
    try {
        return get_region(cx >> 5, cz >> 5)->get_value(cx, cz);
    } catch (RegionDoesNotExist) {
        throw ChunkDoesNotExist("Chunk " + std::to_string(cx) + ", " + std::to_string(cz) + " does not exist.");
    }
}
void AnvilDimensionLayer::set_chunk_data(std::int64_t cx, std::int64_t cz, const AmuletNBT::NamedTag& tag)
{
    return get_region(cx >> 5, cz >> 5, true)->set_value(cx, cz, tag);
}
void AnvilDimensionLayer::delete_chunk(std::int64_t cx, std::int64_t cz)
{
    try {
        get_region(cx >> 5, cz >> 5)->delete_value(cx, cz);
    } catch (RegionDoesNotExist) {
        return;
    }
}
void AnvilDimensionLayer::compact()
{
    for (auto it = all_region_coords(); it != AnvilRegionCoordIterator(); it++) {
        auto [cx, cz] = *it;
        auto region = get_region(cx, cz);
        region->compact();
    }
}

const std::filesystem::path& AnvilDimension::directory() const { return _directory; }
bool AnvilDimension::mcc() const { return _mcc; }

std::vector<std::string> AnvilDimension::layer_names()
{
    std::shared_lock lock(_mutex);
    std::vector<std::string> layers;
    layers.reserve(_layers.size());
    for (const auto& node : _layers) {
        layers.push_back(node.first);
    }
    return layers;
}
bool AnvilDimension::has_layer(const std::string& layer_name)
{
    std::shared_lock lock(_mutex);
    return _layers.contains(layer_name);
}
std::shared_ptr<AnvilDimensionLayer> AnvilDimension::get_layer(const std::string& layer_name)
{
    std::shared_lock lock(_mutex);
    auto it = _layers.find(layer_name);
    if (it == _layers.end()) {
        throw std::invalid_argument("No layer exists with name " + layer_name);
    }
    return it->second;
}

AnvilChunkCoordIterator AnvilDimension::all_chunk_coords() const
{
    return AnvilChunkCoordIterator(_default_layer);
}
bool AnvilDimension::has_chunk(std::int64_t cx, std::int64_t cz) const
{
    return _default_layer->has_chunk(cx, cz);
}
std::map<std::string, AmuletNBT::NamedTag> AnvilDimension::get_chunk_data(std::int64_t cx, std::int64_t cz)
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
void AnvilDimension::delete_chunk(std::int64_t cx, std::int64_t cz)
{
    for (const auto& layer : _layers) {
        layer.second->delete_chunk(cx, cz);
    }
}
void AnvilDimension::compact()
{
    for (const auto& layer : _layers) {
        layer.second->compact();
    }
}

} // namespace Amulet
