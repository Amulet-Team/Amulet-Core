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

VersionNumber JavaRawLevel::_get_data_version()
{
    try {
        auto& root = std::get<AmuletNBT::CompoundTagPtr>(_level_dat.tag_node);
        auto& data = std::get<AmuletNBT::CompoundTagPtr>(root->at("Data"));
        auto& data_version = std::get<AmuletNBT::IntTag>(data->at("DataVersion"));
        return { data_version.value };
    } catch (...) {
        return { -1 };
    }
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
        throw std::runtime_error("Could not open file for reading " + level_dat_path.string());
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

    // Load the data version.
    _data_version = _get_data_version();
}

void JavaRawLevel::_open()
{
    // Reload the metadata to ensure it is up to date.
    reload_metadata();

    // TODO: data pack

    _raw_open_data = std::make_unique<JavaRawLevelOpenData>();
}

void JavaRawLevel::open()
{
    if (is_open()) {
        return;
    }

    // TODO: acquire lock file
    _open();
    opened.emit_async();
}

void JavaRawLevel::_close()
{
    auto raw_open_data = std::move(_raw_open_data);
    // TODO: destroy open data
}

void JavaRawLevel::close()
{
    if (!is_open()) {
        return;
    }
    _close();
    // TODO: Unlock session.lock
    closed.emit_async();
}

void JavaRawLevel::reload()
{
    if (!is_open()) {
        throw std::runtime_error("Level can only be reloaded when it is open.");
    }
    _close();
    _open();
    reloaded.emit_async();
}

const std::filesystem::path& JavaRawLevel::get_path() const
{
    return _path;
}

AmuletNBT::NamedTag JavaRawLevel::get_level_dat() const
{
    return AmuletNBT::deep_copy(_level_dat);
}

void JavaRawLevel::set_level_dat(const AmuletNBT::NamedTag& level_dat)
{
    if (!is_open()) {
        throw std::runtime_error("Level is not open.");
    }
    // Copy the level.dat to internal storage
    _level_dat = AmuletNBT::deep_copy(level_dat);

    // Save to level.dat
    auto level_dat_path = _path / "level.dat";
    // Encode
    std::string encoded_level_dat = AmuletNBT::encode_nbt(_level_dat, std::endian::big, AmuletNBT::utf8_to_mutf8);
    // Compress
    std::string compressed_level_dat;
    AmuletNBT::compress_gzip(encoded_level_dat, compressed_level_dat);
    // Write to file
    std::ofstream level_dat_f(level_dat_path, std::ios::out | std::ios::binary);
    if (!level_dat_f) {
        throw std::runtime_error("Could not open file for writing. " + level_dat_path.string());
    }
    level_dat_f << compressed_level_dat;
    level_dat_f.close();

    // Reload the level if the data version changed.
    if (_data_version != _get_data_version()) {
        reload();
    }
}

std::string JavaRawLevel::get_platform() const
{
    return "java";
}

VersionNumber JavaRawLevel::get_data_version() const
{
    return _data_version;
}

// Get the "Data" CompoundTag from a level.dat NamedTag.
static AmuletNBT::CompoundTag& get_level_dat_data(AmuletNBT::NamedTag& level_dat)
{
    if (!std::holds_alternative<AmuletNBT::CompoundTagPtr>(level_dat.tag_node)) {
        throw std::runtime_error("Level.dat root is not a CompoundTag.");
    }
    auto& root = std::get<AmuletNBT::CompoundTagPtr>(level_dat.tag_node);
    auto it = root->find("Data");
    if (it == root->end()) {
        throw std::runtime_error("Level.dat does not contain \"Data\" entry.");
    }
    if (!std::holds_alternative<AmuletNBT::CompoundTagPtr>(it->second)) {
        throw std::runtime_error("Level.dat[\"Data\"] is not a CompoundTag.");
    }
    return *std::get<AmuletNBT::CompoundTagPtr>(it->second);
}

void JavaRawLevel::set_data_version(const VersionNumber& data_version)
{
    if (data_version.size() != 1) {
        throw std::invalid_argument("Data version must have exactly one value.");
    }
    if (_data_version == data_version) {
        // Data version did not change.
        return;
    }
    auto level_dat = get_level_dat();
    auto& data = get_level_dat_data(level_dat);
    if (data_version[0] == -1) {
        data.erase("DataVersion");
    } else {
        data.insert_or_assign("DataVersion", AmuletNBT::IntTag(static_cast<AmuletNBT::IntTagNative>(data_version[0])));
    }
    set_level_dat(level_dat);
}

std::chrono::system_clock::time_point JavaRawLevel::get_modified_time() const
{

    try {
        auto& root = std::get<AmuletNBT::CompoundTagPtr>(_level_dat.tag_node);
        auto& data = std::get<AmuletNBT::CompoundTagPtr>(root->at("Data"));
        return std::chrono::system_clock::time_point(std::chrono::milliseconds(
            std::get<AmuletNBT::LongTag>(data->at("LastPlayed")).value));
    } catch (...) {
        return std::chrono::system_clock::time_point(std::chrono::milliseconds(0));
    }
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

void JavaRawLevel::set_level_name(const std::string& level_name)
{
    auto level_dat = get_level_dat();
    auto& data = get_level_dat_data(level_dat);
    data.insert_or_assign("LevelName", AmuletNBT::StringTag(level_name));
    set_level_dat(level_dat);
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
        auto& mutex = dimension->get_mutex();
        mutex.lock_shared_read();
        std::shared_lock dimension_lock(mutex, std::adopt_lock);
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
