#include <algorithm>
#include <bit>
#include <fstream>
#include <regex>
#include <stdexcept>
#include <string_view>
#include <vector>

#include <amulet_nbt/nbt_encoding/binary.hpp>

#include <amulet/chunk.hpp>

#include "_region.hpp"

namespace Amulet {

static const std::regex region_regex(R"(r\.(\-?\d+)\.(\-?\d+)\.mca)");

std::pair<std::int64_t, std::int64_t> parse_region_filename(const std::string& filename)
{
    std::smatch match;
    if (!std::regex_search(filename, match, region_regex)) {
        throw std::invalid_argument("Region filename is invalid.");
    }
    return std::make_pair(
        std::stoll(match[1]),
        std::stoll(match[2]));
}

AnvilRegion::AnvilRegion(
    const std::filesystem::path& directory,
    const std::string& file_name,
    std::int64_t rx,
    std::int64_t rz,
    bool mcc)
    : _dir(directory)
    , _path(directory / file_name)
    , _rx(rx)
    , _rz(rz)
    , _mcc(mcc)
{
}

AnvilRegion::AnvilRegion(
    const std::filesystem::path& directory,
    const std::string& file_name,
    const std::pair<std::int64_t, std::int64_t>& region_coordinate,
    bool mcc)
    : AnvilRegion(
        directory,
        file_name,
        region_coordinate.first,
        region_coordinate.second,
        mcc)
{
}

AnvilRegion::AnvilRegion(
    const std::filesystem::path& directory,
    std::int64_t rx,
    std::int64_t rz,
    bool mcc)
    : AnvilRegion(
        directory,
        "r." + std::to_string(rx) + "." + std::to_string(rz) + ".mca",
        rx, rz, mcc)
{
}

AnvilRegion::AnvilRegion(std::filesystem::path path, bool mcc)
    : AnvilRegion(
        path.parent_path(),
        path.filename().string(),
        parse_region_filename(path.filename().string()),
        mcc)
{
}

std::filesystem::path AnvilRegion::path() const
{
    return _path;
}

std::int64_t AnvilRegion::rx() const { return _rx; }
std::int64_t AnvilRegion::rz() const { return _rz; }

static void sanitise_file(const std::filesystem::path& path)
{
    auto size = std::filesystem::file_size(path);
    if (size & 0xFFF) {
        // ensure the file is a multiple of 4096 bytes
        size = (size | 0xFFF) + 1;
        std::filesystem::resize_file(path, size);
    }
    if (size < 0x2000) {
        // if the length of the region file is less than 8KiB extend it to 8KiB
        size = 0x2000;
        std::filesystem::resize_file(path, size);
    }
}

void AnvilRegion::load()
{
    if (_sector_manager) {
        // Already loaded.
        return;
    }

    // Load the region data
    _sector_manager = SectorManager(0, 0x2000);
    _sector_manager->reserve(Sector(0, 0x2000));

    if (std::filesystem::is_regular_file(_path)) {
        sanitise_file(_path);
        std::ifstream f(_path, std::ios_base::in | std::ios_base::binary);
        if (!f) {
            throw std::runtime_error("Could not open file " + _path.string());
        }
        // Read the location table header.
        std::vector<std::uint32_t> location_table(1024);
        f.read(reinterpret_cast<char*>(location_table.data()), 4096);
        if (std::endian::native == std::endian::little) {
            // Raw data is big endian. Convert to little.
            for (auto& v : location_table) {
                char* vv = reinterpret_cast<char*>(&v);
                std::reverse(vv, vv + 4);
            }
        }
        for (size_t cx = 0; cx < 32; cx++) {
            for (size_t cz = 0; cz < 32; cz++) {
                const auto& sector_data = location_table[cx * 32 + cz];
                if (sector_data) {
                    size_t sector_offset = (sector_data >> 8) * 0x1000;
                    size_t sector_size = (sector_data & 0xFF) * 0x1000;
                    Sector sector(sector_offset, sector_offset + sector_size);
                    _sector_manager->reserve(sector);
                    _chunk_locations.emplace(std::make_pair(
                        std::make_pair(
                            cx + _rx * 32, cz + _rz * 32),
                        sector));
                }
            }
        }
    }
}

// void AnvilRegion::all_coords();

bool AnvilRegion::has_data(std::uint8_t cx, std::uint8_t cz)
{
    std::lock_guard lock(mutex);
    load();
    return _chunk_locations.contains(std::make_pair(cx, cz));
};

static AmuletNBT::NamedTag decompress(char compression_type, const std::string_view& data)
{
    switch (compression_type) {
    case 1: // GZIP
    case 2: // Deflate
    case 3: // None
    case 4: // LZ4
    default:
        throw std::runtime_error("Unknown chunk compression format " + std::to_string(static_cast<std::int16_t>(compression_type)));
    }
    // AmuletNBT::read_nbt();
}

AmuletNBT::NamedTag AnvilRegion::get_data(std::uint8_t cx, std::uint8_t cz)
{
    std::lock_guard lock(mutex);
    load();
    auto it = _chunk_locations.find(std::make_pair(cx, cz));
    if (it == _chunk_locations.end()) {
        throw ChunkDoesNotExist("Chunk " + std::to_string(cx) + ", " + std::to_string(cz) + "does not exist.");
    }
    std::ifstream regionf(_path, std::ios_base::in | std::ios_base::binary);
    if (!regionf) {
        throw std::runtime_error("Could not open file " + _path.string());
    }
    regionf.seekg(it->second.start);
    if (!regionf) {
        throw std::runtime_error("Failed seeking.");
    }

    // Read the size of the buffer.
    std::uint32_t buffer_size;
    regionf.read(reinterpret_cast<char*>(&buffer_size), sizeof(std::uint32_t));
    if (!regionf) {
        throw std::runtime_error("Failed reading size.");
    }
    if (std::endian::native == std::endian::little) {
        // Raw data is big endian. Convert to little.
        char* vv = reinterpret_cast<char*>(&buffer_size);
        std::reverse(vv, vv + 4);
    }

    // Read the buffer.
    std::string buffer(buffer_size, 0);
    regionf.read(buffer.data(), buffer_size);
    if (!regionf) {
        throw std::runtime_error("Failed reading buffer.");
    }

    if (_mcc && buffer[0] & 128) {
        // mcc files are supported and external bit is set.
        std::filesystem::path mcc_path = _dir / ("c." + std::to_string(cx) + "." + std::to_string(cz) + ".mcc");
        std::ifstream mccf(mcc_path, std::ios_base::in | std::ios_base::binary);
        if (!mccf) {
            throw std::runtime_error("Could not open file " + mcc_path.string());
        }
        std::stringstream mccbuffer;
        mccbuffer << mccf.rdbuf();
        return decompress(buffer[0] & 127, mccbuffer.str());
    } else {
        return decompress(buffer[0], std::string_view(buffer).substr(1));
    }
};

void AnvilRegion::set_data(std::uint8_t cx, std::uint8_t cz, const AmuletNBT::NamedTag& tag)
{
    std::lock_guard lock(mutex);
    load();
    throw std::runtime_error("NotImplemented");
};

void AnvilRegion::delete_data(std::uint8_t cx, std::uint8_t cz)
{
    std::lock_guard lock(mutex);
    load();
    throw std::runtime_error("NotImplemented");
};

void AnvilRegion::compact()
{
    std::lock_guard lock(mutex);
    load();
    throw std::runtime_error("NotImplemented");
};

} // namespace Amulet
