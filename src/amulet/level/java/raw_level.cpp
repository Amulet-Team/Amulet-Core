#include <bit>
#include <filesystem>
#include <fstream>
#include <memory>
#include <stdexcept>
#include <variant>

#include <amulet_nbt/nbt_encoding/binary.hpp>
#include <amulet_nbt/string_encoding.hpp>
#include <amulet_nbt/tag/copy.hpp>
#include <amulet_nbt/zlib.hpp>

#include "raw_level.hpp"

namespace Amulet {

std::unique_ptr<JavaRawLevel> JavaRawLevel::load(const std::filesystem::path& path)
{
    if (!std::filesystem::is_directory(path)) {
        throw std::invalid_argument("path must be a directory.");
    }
    std::unique_ptr<JavaRawLevel> self(new JavaRawLevel(path));
    self->reload_metadata();
    return self;
}

// Create a new Java level and create a JavaRawLevel instance for it.
std::unique_ptr<JavaRawLevel> JavaRawLevel::create(const JavaCreateArgsV1&)
{
    throw std::runtime_error("NotImplementedError");
}

OrderedMutex& JavaRawLevel::get_mutex()
{
    return _public_mutex;
}

bool JavaRawLevel::is_open() const
{
    return bool(_raw_open_data);
}

void JavaRawLevel::reload_metadata()
{
    if (is_open()) {
        throw std::runtime_error("Cannot reload metadata while the level is open.");
    }

    // Load the level.dat
    auto level_dat_path = _path / "level.dat";
    // Open the file
    std::ifstream level_dat_f(level_dat_path, std::ios::in | std::ios::binary);
    if (!level_dat_f) {
        throw std::runtime_error("Could not open file " + level_dat_path.string());
    }
    // Find the file length
    level_dat_f.seekg(0, std::ios::end);
    size_t level_dat_size = level_dat_f.tellg();
    level_dat_f.seekg(0);
    // Read the file
    std::string level_dat(level_dat_size, 0);
    level_dat_f.read(&level_dat[0], level_dat_size);
    // Decompress the file
    std::string decompressed_level_dat;
    AmuletNBT::decompress_zlib_gzip(level_dat, decompressed_level_dat);
    // Decode the binary NBT.
    _level_dat = AmuletNBT::decode_nbt(decompressed_level_dat, std::endian::big, AmuletNBT::mutf8_to_utf8);

    // Set the data version.
    try {
        auto& root = std::get<AmuletNBT::CompoundTagPtr>(_level_dat.tag_node);
        auto& data = std::get<AmuletNBT::CompoundTagPtr>(root->at("Data"));
        auto& data_version = std::get<AmuletNBT::IntTag>(data->at("DataVersion"));
        _data_version = { data_version.value };
    } catch (...) {
        _data_version = { -1 };
    }
}

void JavaRawLevel::open()
{
    throw std::runtime_error("NotImplementedError");
}

void JavaRawLevel::close()
{
    throw std::runtime_error("NotImplementedError");
}

const std::filesystem::path& JavaRawLevel::get_path() const
{
    return _path;
}

AmuletNBT::NamedTag JavaRawLevel::get_level_dat() const
{
    return AmuletNBT::deep_copy(_level_dat);
}

void JavaRawLevel::set_level_dat(const AmuletNBT::NamedTag&)
{
    throw std::runtime_error("NotImplementedError");
}

std::string JavaRawLevel::get_platform() const
{
    return "java";
}

VersionNumber JavaRawLevel::get_data_version() const
{
    return _data_version;
}

void JavaRawLevel::set_data_version(const VersionNumber&)
{
    throw std::runtime_error("NotImplementedError");
}

std::chrono::system_clock::time_point JavaRawLevel::get_modified_time() const
{

    throw std::runtime_error("NotImplementedError");
}

std::string JavaRawLevel::get_level_name() const
{
    try {
        auto& root = std::get<AmuletNBT::CompoundTagPtr>(_level_dat.tag_node);
        auto& data = std::get<AmuletNBT::CompoundTagPtr>(root->at("Data"));
        return std::get<AmuletNBT::StringTag>(data->at("LevelName"));
    } catch (...) {
        return "Undefined";
    }
}

void JavaRawLevel::set_level_name(const std::string&)
{
    throw std::runtime_error("NotImplementedError");
}

JavaRawLevelOpenData& JavaRawLevel::_find_dimensions()
{
    auto& raw_open = _get_raw_open();
    std::unique_lock lock(raw_open.dimensions_mutex);
    return raw_open;
}

std::vector<std::string> JavaRawLevel::get_dimension_ids()
{
    auto& raw_open = _find_dimensions();
    std::shared_lock lock(raw_open.dimensions_mutex);
    std::vector<DimensionID> dimension_ids;
    dimension_ids.reserve(raw_open.dimension_ids.size());
    for (auto& [dimension_id, _] : raw_open.dimension_ids) {
        dimension_ids.push_back(dimension_id);
    }
    return dimension_ids;
}

std::shared_ptr<JavaRawDimension> JavaRawLevel::get_dimension(const DimensionID& dimension_id)
{
    auto& raw_open = _find_dimensions();
    std::shared_lock lock(raw_open.dimensions_mutex);
    auto it = raw_open.dimension_ids.find(dimension_id);
    JavaInternalDimensionID internal_dimension_id = (it == raw_open.dimension_ids.end()) ? dimension_id : it->second;
    auto it2 = raw_open.dimensions.find(internal_dimension_id);
    if (it2 == raw_open.dimensions.end()) {
        throw std::invalid_argument("Dimension " + dimension_id + " does not exist.");
    }
    return it2->second;
}

void JavaRawLevel::compact()
{
    auto& raw_open = _find_dimensions();
    std::shared_lock dimensions_lock(raw_open.dimensions_mutex);
    for (const auto& [dimension_id, dimension] : raw_open.dimensions) {
        std::unique_lock dimesion_lock(dimension->mutex());
        dimension->compact();
    }
}

std::shared_ptr<IdRegistry> JavaRawLevel::get_block_id_override()
{
    return _get_raw_open().block_id_override;
}

std::shared_ptr<IdRegistry> JavaRawLevel::get_biome_id_override()
{
    return _get_raw_open().biome_id_override;
}

} // namespace Amulet
