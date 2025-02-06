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

#include <lz4.h>
#include <zlib.h>

#include <amulet_nbt/nbt_encoding/binary.hpp>

#include <amulet/chunk.hpp>
#include <amulet/dll.hpp>

#include "region.hpp"

using namespace AmuletNBT;

namespace Amulet {

template <typename T>
static void little_endian_swap(T& value)
{
    if constexpr (std::endian::native != std::endian::little) {
        char* vv = reinterpret_cast<char*>(&value);
        std::reverse(vv, vv + sizeof(T));
    }
}

template <typename T>
static void big_endian_swap(T& value)
{
    if constexpr (std::endian::native != std::endian::big) {
        char* vv = reinterpret_cast<char*>(&value);
        std::reverse(vv, vv + sizeof(T));
    }
}

static const std::uint64_t SectorSize = 0x1000;
static const std::uint64_t MaxRegionSize = SectorSize * 255; // The maximum size data in the region file can be

static const std::regex region_regex(R"(r\.(\-?\d+)\.(\-?\d+)\.mca)");

static LRICache<size_t, std::shared_ptr<AnvilRegion::FileCloser>> region_file_cache(64);

std::pair<std::int64_t, std::int64_t> parse_region_filename(const std::string& filename)
{
    std::smatch match;
    if (!std::regex_search(filename, match, region_regex)) {
        throw std::invalid_argument("Region filename is invalid.");
    }
    return std::make_pair(std::stoll(match[1]), std::stoll(match[2]));
}

// Constructors.
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
    , _shared(std::make_shared<AnvilRegion::Shared>())
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

AnvilRegion::~AnvilRegion()
{
    close();
}

// A mutex which can be used to synchronise calls.
Amulet::OrderedMutex& AnvilRegion::mutex() const { return _shared->public_mutex; }

// The path of the region file.
// Thread safe.
std::filesystem::path AnvilRegion::path() const { return _path; }

// The region x coordinate of the file.
// Thread safe.
std::int64_t AnvilRegion::rx() const { return _rx; }

// The region z coordinate of the file.
// Thread safe.
std::int64_t AnvilRegion::rz() const { return _rz; }

// Create the region file.
// Internal lock required.
void AnvilRegion::create_region_file()
{
    auto& regionf = _shared->regionf;
    regionf.open(_path, std::ios::in | std::ios::out | std::ios::binary | std::ios::trunc);
    if (!regionf) {
        throw std::runtime_error("Could not open file " + _path.string());
    }
    std::string padding(SectorSize * 2, 0);
    regionf.write(padding.data(), padding.size());
}

// Open the region file and fix any size issues.
// Internal lock required.
void AnvilRegion::open_region_file()
{
    auto& regionf = _shared->regionf;
    regionf.open(_path, std::ios::in | std::ios::out | std::ios::binary);
    if (!regionf) {
        throw std::runtime_error("Could not open file " + _path.string());
    }
    regionf.seekp(0, std::ios::end);
    size_t file_size = regionf.tellp();
    if (file_size < SectorSize * 2) {
        // if the length of the region file is less than 8KiB extend it to 8KiB
        std::string padding(SectorSize * 2 - file_size, 0);
        regionf.write(padding.data(), padding.size());
    } else if (file_size & 0xFFF) {
        // ensure the file is a multiple of 4096 bytes
        std::string padding((file_size | 0xFFF) + 1 - file_size, 0);
        regionf.write(padding.data(), padding.size());
    }
}

// Create or open the region file if it is closed.
// Internal lock required.
void AnvilRegion::create_open_region_file_if_closed()
{
    if (!_shared->regionf.is_open()) {
        if (std::filesystem::is_regular_file(_path)) {
            open_region_file();
        } else {
            create_region_file();
        }
    }
}

// Read the header data into memory.
// Internal lock required.
void AnvilRegion::read_file_header()
{
    if (_sector_manager) {
        // Already loaded.
        return;
    }

    if (destroyed) {
        throw std::runtime_error("This region instance has been destroyed.");
    }

    // Load the region data
    _sector_manager = SectorManager(0, SectorSize * 2);
    _sector_manager->reserve(Sector(0, SectorSize * 2));

    if (std::filesystem::is_regular_file(_path)) {
        auto& regionf = _shared->regionf;
        if (!regionf.is_open()) {
            open_region_file();
        }
        // Read the location table header.
        regionf.seekg(0);
        std::vector<std::uint32_t> location_table(1024);
        regionf.read(reinterpret_cast<char*>(location_table.data()), 4096);
        // Convert from big endian to native endianness
        for (auto& v : location_table) {
            big_endian_swap(v);
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

// Close the file object.
// This is automatically called when the instance is destroyed but may be called earlier.
// Internal lock required.
void AnvilRegion::_close()
{
    _shared->regionf.close();
    std::lock_guard lock(region_file_cache.mutex);
    region_file_cache.remove(reinterpret_cast<size_t>(this));
}

// Close the file object if open.
// This is automatically called when the instance is destroyed but may be called earlier.
// Internal lock required.
void AnvilRegion::_close_if_open()
{
    if (_shared->regionf.is_open()) {
        _close();
    } else {
        std::lock_guard lock(region_file_cache.mutex);
        region_file_cache.remove(reinterpret_cast<size_t>(this));
    }
}

// Close the file object if open.
// This is automatically called when the instance is destroyed but may be called earlier.
// Thread safe.
void AnvilRegion::close()
{
    std::lock_guard lock(_shared->mutex);
    _close_if_open();
}

// Destroy the instance.
// Calls made after this will fail.
// This may only be called by the owner of the instance.
// External unique lock required.
void AnvilRegion::destroy()
{
    std::lock_guard lock(_shared->mutex);
    _close_if_open();
    _sector_manager = std::nullopt;
    _chunk_locations.clear();
    destroyed = true;
}

// Get the coordinates of all values in the region file.
// Coordinates are in world space.
// External shared read lock required.
// External shared read-only lock optional.
std::vector<std::pair<std::int64_t, std::int64_t>> AnvilRegion::get_coords()
{
    std::lock_guard lock(_shared->mutex);
    auto closer = _get_file_closer();
    read_file_header();
    std::vector<std::pair<std::int64_t, std::int64_t>> coords;
    coords.reserve(_chunk_locations.size());
    for (const auto& it : _chunk_locations) {
        coords.push_back(it.first);
    }
    return coords;
}

// Is the coordinate in the region.
// This returns true even if there is no value for the coordinate.
// Coordinates are in world space.
// Thread safe.
bool AnvilRegion::contains(std::int64_t cx, std::int64_t cz) const
{
    return _rx * 32 <= cx && cx < (_rx + 1) * 32 && _rz * 32 <= cz && cz < (_rz + 1) * 32;
}

void AnvilRegion::validate_coord(std::int64_t cx, std::int64_t cz) const
{
    if (!contains(cx, cz)) {
        throw std::invalid_argument(
            "Chunk coordinate " + std::to_string(cx) + ", " + std::to_string(cz) + " is not in region " + std::to_string(_rx) + ", " + std::to_string(_rz));
    }
}

// Is there a value stored for this coordinate.
// Coordinates are in world space.
// External shared read lock required.
// External shared read-only lock optional.
bool AnvilRegion::has_value(std::int64_t cx, std::int64_t cz)
{
    validate_coord(cx, cz);
    std::lock_guard lock(_shared->mutex);
    auto closer = _get_file_closer();
    read_file_header();
    return _chunk_locations.contains(std::make_pair(cx, cz));
}

// Decompress zlib or gzip compressed data from src into dst.
static void decompress_zlib(const std::string_view src, std::string& dst)
{
    z_stream stream = {};
    stream.next_in = reinterpret_cast<z_const Bytef*>(src.data());
    stream.avail_in = static_cast<uInt>(src.size());

    switch (inflateInit2(&stream, 32 + MAX_WBITS)) {
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

static const std::string LZ4_MAGIC = "LZ4Block";
static const char COMPRESSION_METHOD_RAW = 0x10;
static const char COMPRESSION_METHOD_LZ4 = 0x20;

// Decompress lz4 compressed data from src into dst.
static void decompress_lz4(const std::string_view src, std::string& dst)
{
    // https://github.com/lz4/lz4-java/blob/7c931bef32d179ec3d3286ee71638b23ebde3459/src/java/net/jpountz/lz4/LZ4BlockInputStream.java#L200
    size_t index = 0;
    while (index < src.size()) {
        if (src.size() < index + 21) {
            throw std::invalid_argument("Corrupt lz4 data. Needed 21 bytes for the header.");
        }
        const std::string_view magic = src.substr(index, 8);
        if (magic != LZ4_MAGIC) {
            throw std::invalid_argument("LZ4 compressed block does not start with LZ4Block.");
        }
        char compression_method = src[index + 8] & 0xF0;
        std::int32_t compressed_length = *reinterpret_cast<const std::int32_t*>(&src[index + 9]);
        little_endian_swap(compressed_length);
        std::int32_t original_length = *reinterpret_cast<const std::int32_t*>(&src[index + 13]);
        little_endian_swap(original_length);
        index += 21;
        if (
            original_length < 0
            || compressed_length < 0
            || (original_length == 0 and compressed_length != 0)
            || (original_length != 0 and compressed_length == 0)) {
            throw std::invalid_argument("LZ4 compressed block is corrupted.");
        }
        switch (compression_method) {
        case COMPRESSION_METHOD_RAW: {
            if (original_length != compressed_length) {
                throw std::invalid_argument("LZ4 compressed block is corrupted.");
            }
            dst.append(src.substr(index, original_length));
            index += original_length;
            break;
        }
        case COMPRESSION_METHOD_LZ4: {
            size_t buf_index = dst.size();
            dst.resize(dst.size() + original_length);
            LZ4_decompress_safe(&src[index], &dst[buf_index], compressed_length, original_length);
            index += compressed_length;
            break;
        }
        default:
            throw std::invalid_argument("LZ4 compressed block is corrupted.");
        }
    }
}

// Decompress the data according to the compression type
static NamedTag decompress(char compression_type, const std::string_view& data)
{
    switch (compression_type) {
    case 1: // GZIP
    case 2: // Deflate
    {
        std::string dst;
        decompress_zlib(data, dst);
        return decode_nbt(dst, std::endian::big, mutf8_to_utf8);
    }
    case 3: // None
        return decode_nbt(data, std::endian::big, mutf8_to_utf8);
    case 4: // LZ4
    {
        std::string dst;
        decompress_lz4(data, dst);
        return decode_nbt(dst, std::endian::big, mutf8_to_utf8);
    }
    default:
        throw std::runtime_error("Unknown chunk compression format " + std::to_string(static_cast<std::int16_t>(compression_type)));
    }
}

// Get the value for this coordinate.
// Coordinates are in world space.
// External shared read lock required.
NamedTag AnvilRegion::get_value(std::int64_t cx, std::int64_t cz)
{
    validate_coord(cx, cz);
    std::lock_guard lock(_shared->mutex);
    auto closer = _get_file_closer();
    read_file_header();
    auto it = _chunk_locations.find(std::make_pair(cx, cz));
    if (it == _chunk_locations.end()) {
        throw ChunkDoesNotExist("Chunk " + std::to_string(cx) + ", " + std::to_string(cz) + " does not exist.");
    }
    create_open_region_file_if_closed();
    auto& regionf = _shared->regionf;
    if (!regionf.seekg(it->second.start)) {
        throw std::runtime_error("Failed seeking.");
    }

    // Read the size of the buffer.
    std::uint32_t buffer_size;
    if (!regionf.read(reinterpret_cast<char*>(&buffer_size), sizeof(std::uint32_t))) {
        throw std::runtime_error("Failed reading size.");
    }
    big_endian_swap(buffer_size);

    // Read the buffer.
    std::string buffer(buffer_size, 0);
    if (!regionf.read(buffer.data(), buffer_size)) {
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

// Set chunk data.
// Internal lock required.
// Caller must ensure the file is open.
template <typename T>
void AnvilRegion::_set_data(std::int64_t cx, std::int64_t cz, T data)
{
    auto& regionf = _shared->regionf;
    // Find the old sector
    std::optional<Sector> old_sector;
    auto old_sector_it = _chunk_locations.find(std::make_pair(cx, cz));
    if (old_sector_it != _chunk_locations.end()) {
        old_sector = old_sector_it->second;
        _chunk_locations.erase(old_sector_it);
    }

    bool mcc_overwritten = false;

    std::uint32_t location = 0;
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
        big_endian_swap(data_size_buffer);
        regionf.write(reinterpret_cast<char*>(&data_size_buffer), 4);
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
        big_endian_swap(location);
    }

    // Write header data
    regionf.seekp(4 * (cx - _rx * 32 + (cz - _rz * 32) * 32));
    regionf.write(reinterpret_cast<char*>(&location), 4);
    regionf.seekg(SectorSize - 4, std::ios::cur);
    std::uint32_t t = static_cast<std::uint32_t>(std::time(NULL));
    big_endian_swap(t);
    regionf.write(reinterpret_cast<char*>(&t), 4);

    // Only do this after updating the header so that the file is always in a valid state.
    if (old_sector) {
        if (_mcc && !mcc_overwritten) {
            // Delete the old external mcc file
            std::filesystem::path mcc_path = _dir / ("c." + std::to_string(cx) + "." + std::to_string(cz) + ".mcc");
            if (std::filesystem::is_regular_file(mcc_path)) {
                std::filesystem::remove(mcc_path);
            }
        }
        // Free the old sector
        _sector_manager->free(*old_sector);
    }
}

// Set the value for this coordinate.
// Coordinates are in world space.
// External shared read-write lock required.
void AnvilRegion::set_value(std::int64_t cx, std::int64_t cz, const NamedTag& tag)
{
    validate_coord(cx, cz);
    // Encode the tag
    BinaryWriter writer(
        std::endian::big,
        &utf8_to_mutf8);
    encode_nbt(writer, tag);
    const std::string& bnbt = writer.getBuffer();

    // Get the size of the data
    if (std::numeric_limits<uLong>::max() < bnbt.size()) {
        throw std::runtime_error("tag is too large to compress.");
    }
    uLong source_length = static_cast<uLong>(bnbt.size());
    uLongf compressed_size = compressBound(source_length);

    // Create the output string
    std::string data;
    data.resize(compressed_size + 1);
    data[0] = 2;

    if (compress(reinterpret_cast<Bytef*>(&data[1]), &compressed_size, reinterpret_cast<const Bytef*>(bnbt.data()), source_length) != Z_OK) {
        throw std::runtime_error("Error compressing data.");
    };
    data.resize(compressed_size + 1);

    if (!_mcc && data.size() + 4 > MaxRegionSize) {
        // Skip saving large chunks if mcc files are not enabled.
        // TODO: add an error message.
        // f"Could not save data {cx},{cz} in region file {self._path} because it was too large."
        return;
    }

    std::lock_guard lock(_shared->mutex);
    auto closer = _get_file_closer();
    read_file_header();
    create_open_region_file_if_closed();
    _set_data<std::string_view>(cx, cz, data);
}

// Delete the chunk data.
// Coordinates are in world space.
// External shared read-write lock required.
void AnvilRegion::delete_value(std::int64_t cx, std::int64_t cz)
{
    validate_coord(cx, cz);
    std::lock_guard lock(_shared->mutex);
    if (!std::filesystem::is_regular_file(_path)) {
        // Do nothing if there is no file.
        return;
    }
    auto closer = _get_file_closer();
    read_file_header();
    create_open_region_file_if_closed();
    _set_data<std::nullopt_t>(cx, cz, std::nullopt);
}

// Delete multiple chunk's data.
// Coordinates are in world space.
// External shared read-write lock required.
void AnvilRegion::delete_batch(std::vector<std::pair<std::int64_t, std::int64_t>>& coords)
{
    std::lock_guard lock(_shared->mutex);
    if (!std::filesystem::is_regular_file(_path)) {
        // Do nothing if there is no file.
        return;
    }
    auto closer = _get_file_closer();
    read_file_header();
    create_open_region_file_if_closed();

    for (const auto& [cx, cz] : coords) {
        if (contains(cx, cz)) {
            _set_data<std::nullopt_t>(cx, cz, std::nullopt);
        }
    }
}

// Compact the region file.
// Defragments the file and deletes unused space.
// If there are no chunks remaining in the region file it will be deleted.
// Thread safe.
void AnvilRegion::compact()
{
    std::lock_guard lock(_shared->mutex);
    if (!std::filesystem::is_regular_file(_path)) {
        // Do nothing if there is no file.
        return;
    }

    auto closer = _get_file_closer();
    read_file_header();
    if (_chunk_locations.empty()) {
        // No chunks in the region file. Delete it.
        _close_if_open();
        std::filesystem::remove(_path);
        return;
    }

    // Sort by start position.
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

    create_open_region_file_if_closed();
    auto& regionf = _shared->regionf;

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
            big_endian_swap(location);
            regionf.seekp(header_index);
            regionf.write(reinterpret_cast<char*>(&location), 4);

            // Update internal state
            _chunk_locations[chunk_coordinate] = new_sector;
            _sector_manager->free(sector);
        }
    }
    _close();
    // Delete any unused data at the end.
    std::filesystem::resize_file(_path, file_position);
}

std::shared_ptr<AnvilRegion::FileCloser> AnvilRegion::_get_file_closer()
{
    std::shared_ptr<AnvilRegion::FileCloser> closer = _closer.lock();
    if (!closer) {
        closer = std::make_shared<AnvilRegion::FileCloser>(_shared);
        _closer = closer;
    }
    std::lock_guard lock(region_file_cache.mutex);
    region_file_cache.add(reinterpret_cast<size_t>(this), closer);
    return closer;
}

std::shared_ptr<AnvilRegion::FileCloser> AnvilRegion::get_file_closer()
{
    std::lock_guard lock(_shared->mutex);
    return _get_file_closer();
}

AnvilRegion::FileCloser::FileCloser(std::shared_ptr<Shared> shared)
    : _shared(shared)
{
}
AnvilRegion::FileCloser::~FileCloser()
{
    std::lock_guard lock(_shared->mutex);
    if (_shared->regionf.is_open()) {
        _shared->regionf.close();
    }
}

} // namespace Amulet
