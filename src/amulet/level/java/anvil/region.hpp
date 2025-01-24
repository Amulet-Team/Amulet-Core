#pragma once

#include <cstdint>
#include <filesystem>
#include <fstream>
#include <list>
#include <map>
#include <mutex>
#include <optional>
#include <string>
#include <utility>
#include <vector>

#include <amulet/dll.hpp>
#include <amulet_nbt/tag/named_tag.hpp>

#include "sector_manager.hpp"

namespace Amulet {

template <typename K, typename V>
class LRICache {
private:
    size_t _max_size;
    std::list<std::pair<K, V>> _values;
    std::map<K, typename std::list<std::pair<K, V>>::iterator> _map;
    void remove_extra()
    {
        while (_max_size < _values.size()) {
            _map.erase(_values.front().first);
            _values.pop_front();
        }
    }

public:
    LRICache(size_t max_size)
        : _max_size(max_size) {};
    size_t max_size() const { return _max_size; };
    void set_max_size(size_t max_size)
    {
        _max_size = max_size;
        remove_extra();
    };
    void add(const K& k, const V& v)
    {
        auto it = _map.find(k);
        if (it == _map.end()) {
            // Create and insert the value
            _values.emplace_back(k, v);
            _map.emplace(k, --_values.end());
            remove_extra();
        } else {
            // Move the value to the end.
            _values.splice(_values.end(), _values, it->second);
        }
    };
    void remove(const K& k)
    {
        auto it = _map.find(k);
        if (it != _map.end()) {
            _values.erase(it->second);
            _map.erase(it);
        }
    }
};

AMULET_CORE_DLLX std::pair<std::int64_t, std::int64_t> parse_region_filename(const std::string& filename);

// A class to read and write Minecraft Java Edition Region files.
// Only one instance should exist per region file at any given time otherwise bad things may happen.
class AnvilRegion : public std::enable_shared_from_this<AnvilRegion> {
public:
    // A class to manage closing the region file.
    // When the instance is deleted the region file will be closed.
    // The region file can be manually closed before this is deleted.
    class FileCloser {
    private:
        // A weak reference to the region
        std::weak_ptr<AnvilRegion> _region;

    public:
        AMULET_CORE_DLLX FileCloser(std::weak_ptr<AnvilRegion> region);
        AMULET_CORE_DLLX ~FileCloser();
    };

    friend FileCloser;

private:
    // The directory the region file is in.
    std::filesystem::path _dir;
    std::filesystem::path _path;

    // The region coordinates.
    std::int64_t _rx;
    std::int64_t _rz;

    // Is support for .mcc files enabled.
    bool _mcc;

    // A class to track which sectors are reserved.
    // Null if it has not been synchronised with the file.
    std::optional<SectorManager> _sector_manager;

    // A map from the chunk coordinate to the location on disk
    std::map<std::pair<std::int64_t, std::int64_t>, Sector> _chunk_locations;

    // The region file handle
    std::fstream regionf;

    // Region file closer
    std::weak_ptr<FileCloser> _closer;

    // Has the region been marked as destroyed.
    bool destroyed = false;

    // This mutex must be acquired to access the container data or the file.
    std::recursive_mutex mutex;

    AnvilRegion(const std::filesystem::path& directory, const std::string& file_name, const std::pair<std::int64_t, std::int64_t>& region_coordinate, bool mcc = false);

    // Load data from the region file if it exists.
    // Lock must be acquired before calling this.
    void read_file_header();

    // Create the region file.
    // Lock must be acquired before calling this.
    void create_region_file();

    // Open the region file and fix any size issues.
    // Lock must be acquired before calling this.
    void open_region_file();

    // Create or open the region file if it is closed.
    // Lock must be acquired before calling this.
    void create_open_region_file_if_closed();

    void validate_coord(std::int64_t cx, std::int64_t cz);
    template <typename T>
    void _set_data(std::int64_t cx, std::int64_t cz, T data);

    // Get the object responsible for closing the region file.
    // When this object is deleted it will close the region file
    // This means that holding a reference to this will delay when the region file is closed.
    // The region file may still be closed manually before this object is deleted.
    // Lock must be acquired before calling this.
    AMULET_CORE_DLLX std::shared_ptr<FileCloser> _get_file_closer();

    // Close the file object if open.
    // This is automatically called when the instance is destroyed but may be called earlier.
    // Lock must be acquired before calling this.
    void _close();
    void _close_if_open();

public:
    // Constructors.
    AMULET_CORE_DLLX AnvilRegion(const std::filesystem::path& directory, const std::string& file_name, std::int64_t rx, std::int64_t rz, bool mcc = false);
    AMULET_CORE_DLLX AnvilRegion(const std::filesystem::path& directory, std::int64_t rx, std::int64_t rz, bool mcc = false);
    AMULET_CORE_DLLX AnvilRegion(std::filesystem::path path, bool mcc = false);

    // The path of the region file. Thread safe.
    AMULET_CORE_DLLX std::filesystem::path path() const;

    // The region x coordinate of the file. Thread safe.
    AMULET_CORE_DLLX std::int64_t rx() const;

    // The region z coordinate of the file. Thread safe.
    AMULET_CORE_DLLX std::int64_t rz() const;

    // Get the coordinates of all values in the region file.
    // Coordinates are in world space.
    // Thread safe.
    AMULET_CORE_DLLX std::vector<std::pair<std::int64_t, std::int64_t>> get_coords();

    // Is the coordinate in the region.
    // This returns true even if there is no value for the coordinate.
    // Coordinates are in world space.
    // Thread safe.
    AMULET_CORE_DLLX bool contains(std::int64_t cx, std::int64_t cz);

    // Is there a value stored for this coordinate.
    // Coordinates are in world space.
    // Thread safe.
    AMULET_CORE_DLLX bool has_value(std::int64_t cx, std::int64_t cz);

    // Get the value for this coordinate.
    // Coordinates are in world space.
    // Thread safe.
    AMULET_CORE_DLLX AmuletNBT::NamedTag get_value(std::int64_t cx, std::int64_t cz);
    // AMULET_CORE_DLLX std::vector<std::optional<AmuletNBT::NamedTag>> get_batch(std::vector<std::pair<std::int64_t, std::int64_t>>& coords);

    // Set the value for this coordinate.
    // Coordinates are in world space.
    // Thread safe.
    AMULET_CORE_DLLX void set_value(std::int64_t cx, std::int64_t cz, const AmuletNBT::NamedTag& tag);
    // AMULET_CORE_DLLX void set_batch(std::vector<std::tuple<std::int64_t, std::int64_t, AmuletNBT::NamedTag>>& batch);

    // Delete the chunk data.
    // Coordinates are in world space.
    // Thread safe.
    AMULET_CORE_DLLX void delete_value(std::int64_t cx, std::int64_t cz);
    AMULET_CORE_DLLX void delete_batch(std::vector<std::pair<std::int64_t, std::int64_t>>& coords);

    // Compact the region file.
    // Defragments the file and deletes unused space.
    // If there are no chunks remaining in the region file it will be deleted.
    // Thread safe.
    AMULET_CORE_DLLX void compact();

    // Close the file object if open.
    // This is automatically called when the instance is destroyed but may be called earlier.
    // Thread safe.
    AMULET_CORE_DLLX void close();

    // Destroy the instance.
    // Calls made after this will fail.
    // This may only be called by the owner of the instance.
    // Thread safe.
    AMULET_CORE_DLLX void destroy();

    // Get the object responsible for closing the region file.
    // When this object is deleted it will close the region file
    // This means that holding a reference to this will delay when the region file is closed.
    // The region file may still be closed manually before this object is deleted.
    // Thread safe.
    AMULET_CORE_DLLX std::shared_ptr<FileCloser> get_file_closer();
};

} // namespace Amulet
