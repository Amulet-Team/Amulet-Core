#include <algorithm>
#include <bit>
#include <chrono>
#include <cstdint>
#include <ctime>
#include <fstream>
#include <list>
#include <regex>
#include <set>
#include <stdexcept>
#include <string_view>
#include <vector>

#include <zlib.h>

#include <amulet_nbt/nbt_encoding/binary.hpp>

#include <amulet/chunk.hpp>
#include <amulet/dll.hpp>

#include "_region.hpp"

namespace Amulet {

static const std::uint64_t SectorSize = 0x1000;
static const std::uint64_t MaxRegionSize = SectorSize * 255; // The maximum size data in the region file can be

static const std::regex region_regex(R"(r\.(\-?\d+)\.(\-?\d+)\.mca)");

AMULET_CORE_DLLX std::pair<std::int64_t, std::int64_t> parse_region_filename(const std::string& filename)
{
    std::smatch match;
    if (!std::regex_search(filename, match, region_regex)) {
        throw std::invalid_argument("Region filename is invalid.");
    }
    return std::make_pair(std::stoll(match[1]), std::stoll(match[2]));
}

AMULET_CORE_DLLX AnvilRegion::AnvilRegion(
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

AMULET_CORE_DLLX AnvilRegion::AnvilRegion(
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

AMULET_CORE_DLLX AnvilRegion::AnvilRegion(std::filesystem::path path, bool mcc)
    : AnvilRegion(
          path.parent_path(),
          path.filename().string(),
          parse_region_filename(path.filename().string()),
          mcc)
{
}

AMULET_CORE_DLLX std::filesystem::path AnvilRegion::path() const { return _path; }
AMULET_CORE_DLLX std::int64_t AnvilRegion::rx() const { return _rx; }
AMULET_CORE_DLLX std::int64_t AnvilRegion::rz() const { return _rz; }

static void sanitise_file(const std::filesystem::path& path)
{
    auto size = std::filesystem::file_size(path);
    if (size & 0xFFF) {
        // ensure the file is a multiple of 4096 bytes
        size = (size | 0xFFF) + 1;
        std::filesystem::resize_file(path, size);
    }
    if (size < SectorSize * 2) {
        // if the length of the region file is less than 8KiB extend it to 8KiB
        size = SectorSize * 2;
        std::filesystem::resize_file(path, size);
    }
}

void AnvilRegion::read_file_header()
{
    if (_sector_manager) {
        // Already loaded.
        return;
    }

    // Load the region data
    _sector_manager = SectorManager(0, SectorSize * 2);
    _sector_manager->reserve(Sector(0, SectorSize * 2));

    if (std::filesystem::is_regular_file(_path)) {
        sanitise_file(_path);
        std::ifstream f(_path, std::ios::in | std::ios::binary);
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
                const auto& sector_data = location_table[cx + cz * 32];
                if (sector_data) {
                    size_t sector_offset = (sector_data >> 8) * SectorSize;
                    size_t sector_size = (sector_data & 0xFF) * SectorSize;
                    Sector sector(sector_offset, sector_offset + sector_size);
                    _sector_manager->reserve(sector);
                    _chunk_locations.emplace(std::make_pair(cx + _rx * 32, cz + _rz * 32), sector);
                }
            }
        }
    }
}

AMULET_CORE_DLLX std::vector<std::pair<std::int64_t, std::int64_t>> AnvilRegion::get_coords()
{
    std::lock_guard lock(mutex);
    read_file_header();
    std::vector<std::pair<std::int64_t, std::int64_t>> coords;
    coords.reserve(_chunk_locations.size());
    for (const auto& it : _chunk_locations) {
        coords.push_back(it.first);
    }
    return coords;
}

AMULET_CORE_DLLX bool AnvilRegion::contains(std::int64_t cx, std::int64_t cz)
{
    return _rx * 32 <= cx && cx < (_rx + 1) * 32 && _rz * 32 <= cz && cz < (_rz + 1) * 32;
}

void AnvilRegion::validate_coord(std::int64_t cx, std::int64_t cz)
{
    if (!contains(cx, cz)) {
        throw std::invalid_argument(
            "Chunk coordinate " + std::to_string(cx) + ", " + std::to_string(cz) + " is not in region " + std::to_string(_rx) + ", " + std::to_string(_rz));
    }
}

AMULET_CORE_DLLX bool AnvilRegion::has_value(std::int64_t cx, std::int64_t cz)
{
    validate_coord(cx, cz);
    std::lock_guard lock(mutex);
    read_file_header();
    return _chunk_locations.contains(std::make_pair(cx, cz));
}

static void decompress_zlib(const std::string_view src, std::string& dst)
{
    z_stream stream = {};
    stream.next_in = reinterpret_cast<z_const Bytef*>(src.data());
    stream.avail_in = static_cast<uInt>(src.size());

    switch (inflateInit(&stream)) {
    case Z_MEM_ERROR:
        throw std::bad_alloc();
    case Z_VERSION_ERROR:
        throw std::runtime_error("Incompatible zlib library.");
    case Z_STREAM_ERROR:
        throw std::runtime_error("zlib stream is invalid.");
    }

    const size_t chunk_size = 65536;
    int err;
    do {
        // allocate data after dst
        size_t dst_size = dst.size();
        dst.resize(dst_size + chunk_size);

        // Assign the location to decompress into
        stream.next_out = reinterpret_cast<Bytef*>(&dst[dst_size]);
        stream.avail_out = chunk_size;

        // Decompress
        err = inflate(&stream, Z_NO_FLUSH);

        // Continue until error or end of stream.
    } while (err == Z_OK);

    // Remove unused bytes
    dst.resize(dst.size() - stream.avail_out);
    // Clear stream data
    inflateEnd(&stream);

    switch (err) {
    case Z_STREAM_END:
        return;
    case Z_DATA_ERROR:
        throw std::invalid_argument("Cannot decompress corrupt zlib data.");
    case Z_MEM_ERROR:
        throw std::bad_alloc();
    case Z_STREAM_ERROR:
        throw std::runtime_error("zlib stream is invalid.");
    case Z_BUF_ERROR:
        throw std::runtime_error("Decompression requires a larger buffer than the one provided.");
    default:
        throw std::runtime_error("zlib decompression error.");
    }
}

static AmuletNBT::NamedTag decompress(char compression_type, const std::string_view& data)
{
    switch (compression_type) {
    case 1: // GZIP
        throw std::runtime_error("GZIP compression has not been implemented.");
    case 2: // Deflate
    {
        std::string dst;
        decompress_zlib(data, dst);
        return AmuletNBT::read_nbt(dst, std::endian::big, AmuletNBT::mutf8_to_utf8);
    }
    case 3: // None
        return AmuletNBT::read_nbt(data, std::endian::big, AmuletNBT::mutf8_to_utf8);
    case 4: // LZ4
        throw std::runtime_error("LZ4 compression has not been implemented.");
    default:
        throw std::runtime_error("Unknown chunk compression format " + std::to_string(static_cast<std::int16_t>(compression_type)));
    }
}

AMULET_CORE_DLLX AmuletNBT::NamedTag AnvilRegion::get_value(std::int64_t cx, std::int64_t cz)
{
    validate_coord(cx, cz);
    std::lock_guard lock(mutex);
    read_file_header();
    auto it = _chunk_locations.find(std::make_pair(cx, cz));
    if (it == _chunk_locations.end()) {
        throw ChunkDoesNotExist("Chunk " + std::to_string(cx) + ", " + std::to_string(cz) + "does not exist.");
    }
    std::ifstream regionf(_path, std::ios::in | std::ios::binary);
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
        std::ifstream mccf(mcc_path, std::ios::in | std::ios::binary);
        if (!mccf) {
            throw std::runtime_error("Could not open file " + mcc_path.string());
        }
        std::stringstream mccbuffer;
        mccbuffer << mccf.rdbuf();
        return decompress(buffer[0] & 127, mccbuffer.str());
    } else {
        return decompress(buffer[0], std::string_view(buffer).substr(1));
    }
}

template <typename T>
void AnvilRegion::_set_data(std::fstream& regionf, std::int64_t cx, std::int64_t cz, T data)
{
    // Find the old sector
    std::optional<Sector> old_sector;
    auto old_sector_it = _chunk_locations.find(std::make_pair(cx, cz));
    if (old_sector_it != _chunk_locations.end()) {
        old_sector = old_sector_it->second;
        _chunk_locations.erase(old_sector_it);
    }

    bool mcc_overwritten = false;

    std::uint32_t location = 0;
    char* location_char = reinterpret_cast<char*>(&location);
    if constexpr (std::is_same_v<T, std::string_view>) {
        // Write the new chunk data
        char format_byte = 0;
        if (data.size() + 4 > MaxRegionSize) {
            // save externally (if mcc files are not supported the check at the top will filter large files out)
            mcc_overwritten = true;
            std::filesystem::path mcc_path = _dir / ("c." + std::to_string(cx) + "." + std::to_string(cz) + ".mcc");
            std::ofstream mccf(mcc_path, std::ios::out | std::ios::binary | std::ios::trunc);
            if (!mccf) {
                throw std::runtime_error("Could not open file " + mcc_path.string());
            }
            mccf.write(&data[1], data.size() - 1);
            format_byte = data[0] | 128;
            data = std::string_view(reinterpret_cast<char*>(&format_byte), 1);
        }

        // Find how big the sector needs to be.
        size_t data_size = data.size() + 4;
        size_t sector_length = data_size;
        if (sector_length & 0xFFF) {
            sector_length = (sector_length | 0xFFF) + 1;
        }
        // Reserve a sector large enough to fit the data.
        auto sector = _sector_manager->reserve_space(sector_length);
        if (sector.start & 0xFFF) {
            throw std::runtime_error("Sector size is not a multiple of 0x1000.");
        }
        _chunk_locations.emplace(std::make_pair(cx, cz), sector);
        // Seek to the sector to write to
        regionf.seekp(sector.start);
        // Write the size value
        std::uint32_t data_size_buffer = static_cast<std::uint32_t>(data_size);
        char* size_char = reinterpret_cast<char*>(&data_size_buffer);
        if constexpr (std::endian::native != std::endian::big) {
            std::reverse(size_char, size_char + 4);
        }
        regionf.write(size_char, 4);
        // Write the data
        regionf.write(data.data(), data.size());
        // Pad to sector_length
        size_t pad_size = sector_length - data_size;
        if (pad_size) {
            std::string padding(pad_size, 0);
            regionf.write(padding.data(), pad_size);
        }
        // Create the location value
        location = static_cast<std::uint32_t>((sector.start >> 4) + (sector_length >> 12));
        if constexpr (std::endian::native != std::endian::big) {
            std::reverse(location_char, location_char + 4);
        }
    }

    // Write header data
    regionf.seekp(4 * (cx - _rx * 32 + (cz - _rz * 32) * 32));
    regionf.write(location_char, 4);
    regionf.seekg(SectorSize - 4, std::ios::cur);
    std::uint32_t t = static_cast<std::uint32_t>(std::time(NULL));
    char* t_char = reinterpret_cast<char*>(&t);
    if constexpr (std::endian::native != std::endian::big) {
        std::reverse(t_char, t_char + 4);
    }
    regionf.write(t_char, 4);

    // Only do this after updating the header so that the file is always in a valid state.
    if (old_sector) {
        if (_mcc && !mcc_overwritten) {
            regionf.seekg(old_sector->start + 4);
            std::uint8_t format_byte;
            regionf.read(reinterpret_cast<char*>(&format_byte), 1);
            if (format_byte & 127) {
                // Delete the old external mcc file
                std::filesystem::path mcc_path = _dir / ("c." + std::to_string(cx) + "." + std::to_string(cz) + ".mcc");
                if (std::filesystem::is_regular_file(mcc_path)) {
                    std::filesystem::remove(mcc_path);
                }
            }
        }
        // Free the old sector
        _sector_manager->free(*old_sector);
    }
}

static void open_region_file(std::fstream& regionf, const std::filesystem::path& path) {
    if (std::filesystem::is_regular_file(path)) {
        sanitise_file(path);
        regionf.open(path, std::ios::in | std::ios::out | std::ios::binary);
        if (!regionf) {
            throw std::runtime_error("Could not open file " + path.string());
        }
    } else {
        regionf.open(path, std::ios::in | std::ios::out | std::ios::binary | std::ios::trunc);
        if (!regionf) {
            throw std::runtime_error("Could not open file " + path.string());
        }
        regionf.write(std::string(SectorSize * 2, 0).c_str(), SectorSize * 2);
    }
}

template <typename T>
void AnvilRegion::_set_data(std::int64_t cx, std::int64_t cz, T data)
{
    validate_coord(cx, cz);
    if constexpr (std::is_same_v<T, std::string_view>) {
        if (!_mcc && data.size() + 4 > MaxRegionSize) {
            // Skip saving large chunks if mcc files are not enabled.
            // TODO: add an error message.
            // f"Could not save data {cx},{cz} in region file {self._path} because it was too large."
            return;
        }
    }

    std::lock_guard lock(mutex);

    // Open the file (create if needed)
    read_file_header();
    std::fstream regionf;
    open_region_file(regionf, _path);
    _set_data<T>(regionf, cx, cz, data);
}

AMULET_CORE_DLLX void AnvilRegion::set_value(std::int64_t cx, std::int64_t cz, const AmuletNBT::NamedTag& tag)
{
    // Encode the tag
    AmuletNBT::BinaryWriter writer(
        std::endian::big,
        &AmuletNBT::utf8_to_mutf8);
    AmuletNBT::write_nbt(writer, tag);
    const std::string& bnbt = writer.getBuffer();

    // Get the size of the data
    uLong source_length = bnbt.size();
    uLongf compressed_size = compressBound(source_length);

    // Create the output string
    std::string data;
    data.resize(compressed_size + 1);
    data[0] = 2;

    if (compress(reinterpret_cast<Bytef*>(&data[1]), &compressed_size, reinterpret_cast<const Bytef*>(bnbt.data()), source_length) != Z_OK) {
        throw std::runtime_error("Error compressing data.");
    };
    data.resize(compressed_size + 1);

    _set_data<std::string_view>(cx, cz, data);
}

AMULET_CORE_DLLX void AnvilRegion::delete_value(std::int64_t cx, std::int64_t cz)
{
    _set_data<std::nullopt_t>(cx, cz, std::nullopt);
}

AMULET_CORE_DLLX void AnvilRegion::delete_batch(std::vector<std::pair<std::int64_t, std::int64_t>>& coords)
{
    std::lock_guard lock(mutex);
    
    // Open the file (create if needed)
    read_file_header();
    std::fstream regionf;
    open_region_file(regionf, _path);
    
    for (const auto& [cx, cz] : coords) {
        if (contains(cx, cz)) {
            _set_data<std::nullopt_t>(regionf, cx, cz, std::nullopt);
        }
    }
}

AMULET_CORE_DLLX void AnvilRegion::compact()
{
    std::lock_guard lock(mutex);
    if (!std::filesystem::is_regular_file(_path)) {
        // Do nothing if there is no file.
        return;
    }

    read_file_header();
    if (_chunk_locations.empty()) {
        // No chunks in the region file. Delete it.
        std::filesystem::remove(_path);
        return;
    }

    // Sort by length then start.
    struct SectorStartSort {
        bool operator()(
            const std::tuple<size_t, std::pair<std::int64_t, std::int64_t>, Sector>& a,
            const std::tuple<size_t, std::pair<std::int64_t, std::int64_t>, Sector>& b) const
        {
            return std::get<2>(a).start < std::get<2>(b).start;
        }
    };

    // Generate a list of sectors in sequential order
    // location header index, chunk coordinate, sector
    std::set<
        std::tuple<size_t, std::pair<std::int64_t, std::int64_t>, Sector>,
        SectorStartSort>
        chunk_sectors;
    for (const auto& [coord, sector] : _chunk_locations) {
        chunk_sectors.emplace(
            4 * (coord.first - _rx * 32 + (coord.second - _rz * 32) * 32),
            std::make_pair(coord.first, coord.second),
            sector);
    }

    // Set the position to the end of the header
    size_t file_position = 2 * SectorSize;
    size_t file_end = std::get<2>(*chunk_sectors.rbegin()).stop;

    sanitise_file(_path);
    std::fstream regionf(_path, std::ios::in | std::ios::out | std::ios::binary);
    if (!regionf) {
        throw std::runtime_error("Could not open file " + _path.string());
    }

    while (!chunk_sectors.empty()) {
        // While there are remaining sectors, get the first sector.
        const auto [header_index, chunk_coordinate, sector] = *chunk_sectors.begin();
        chunk_sectors.erase(chunk_sectors.begin());

        if (file_position == sector.start) {
            // There isn't any space before the sector. Do nothing.
            file_position = sector.stop;
        } else {
            // There is space before the sector
            Sector new_sector;
            if (file_position + sector.length() <= sector.start) {
                // There is enough space before the sector to fit the whole sector.
                // Copy it to the new location
                new_sector = Sector(file_position, file_position + sector.length());
                file_position = new_sector.stop;
            } else {
                // There is space before the sector but not enough to fit the sector.
                // Move it to the end for processing later.
                new_sector = Sector(file_end, file_end + sector.length());
                file_end = new_sector.stop;
                chunk_sectors.emplace(header_index, chunk_coordinate, new_sector);
            }

            // Read in the data
            std::string data(sector.length(), 0);
            regionf.seekg(sector.start);
            regionf.read(data.data(), data.size());

            // Reserve and write the data to the new sector
            _sector_manager->reserve(new_sector);
            regionf.seekp(new_sector.start);
            regionf.write(data.data(), data.size());

            // Update the index
            std::uint32_t location = static_cast<std::uint32_t>((new_sector.start >> 4) + (new_sector.length() >> 12));
            char* location_char = reinterpret_cast<char*>(&location);
            if constexpr (std::endian::native != std::endian::big) {
                std::reverse(location_char, location_char + 4);
            }
            regionf.seekp(header_index);
            regionf.write(location_char, 4);

            // Update internal state
            _chunk_locations[chunk_coordinate] = new_sector;
            _sector_manager->free(sector);
        }
    }
    regionf.close();
    // Delete any unused data at the end.
    std::filesystem::resize_file(_path, file_position);
}

} // namespace Amulet
