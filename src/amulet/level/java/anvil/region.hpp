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
#include <amulet/utils/mutex.hpp>
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
    std::mutex mutex;
    LRICache(size_t max_size)
        : _max_size(max_size) {};
    // The current max size value. mutex must be acquired while calling.
    size_t max_size() const { return _max_size; };
    // Set the max size value. mutex must be acquired while calling.
    void set_max_size(size_t max_size)
    {
        _max_size = max_size;
        remove_extra();
    };
    // Add an item. mutex must be acquired while calling.
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
    // Remove an item. mutex must be acquired while calling.
    void remove(const K& k)
    {
        auto it = _map.find(k);
        if (it != _map.end()) {
            _values.erase(it->second);
            _map.erase(it);
        }
    }
};

AMULET_CORE_EXPORT std::pair<std::int64_t, std::int64_t> parse_region_filename(const std::string& filename);

// A class to read and write Minecraft Java Edition Region files.
// Only one instance should exist per region file at any given time otherwise bad things may happen.
// This class is internally thread safe but a public mutex is provided to enable external synchronisation.
// Upstream locks from the level must also be adhered to.
class AnvilRegion {
private:
    // Data shared between the region and closer.
    class Shared {
    public:
        // The region file handle
        std::fstream regionf;
        // This mutex must be acquired to access the container data or the file.
        std::recursive_mutex mutex;
    };

public:
    // A class to manage closing the region file.
    // When the instance is deleted the region file will be closed.
    // The region file can be manually closed before this is deleted.
    class FileCloser {
    private:
        // Data shared between the region and closer.
        std::shared_ptr<Shared> _shared;

    public:
        AMULET_CORE_EXPORT FileCloser(std::shared_ptr<Shared> shared);
        AMULET_CORE_EXPORT ~FileCloser();
    };

    friend FileCloser;

private:
    // The public mutex.
    Amulet::OrderedMutex _public_mutex;

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

    // Mutex for getting the file closer.
    std::mutex _file_closer_mutex;

    // Region file closer
    std::weak_ptr<FileCloser> _closer;

    // Has the region been marked as destroyed.
    bool destroyed = false;

    // Data shared between the region and closer.
    std::shared_ptr<Shared> _shared;

    AnvilRegion(const std::filesystem::path& directory, const std::string& file_name, const std::pair<std::int64_t, std::int64_t>& region_coordinate, bool mcc = false);

    // Load data from the region file if it exists.
    // Internal lock required.
    void read_file_header();

    // Create the region file.
    // Internal lock required.
    void create_region_file();

    // Open the region file and fix any size issues.
    // Internal lock required.
    void open_region_file();

    // Create or open the region file if it is closed.
    // Internal lock required.
    void create_open_region_file_if_closed();

    void validate_coord(std::int64_t cx, std::int64_t cz) const;

    // Set chunk data.
    // Internal lock required.
    // Caller must ensure the file is open.
    template <typename T>
    void _set_data(std::int64_t cx, std::int64_t cz, T data);

    // Close the file object.
    // This is automatically called when the instance is destroyed but may be called earlier.
    // Internal lock required.
    void _close();
    
    // Close the file object if open.
    // This is automatically called when the instance is destroyed but may be called earlier.
    // Internal lock required.
    void _close_if_open();

public:
    // Constructors.
    AnvilRegion() = delete;
    AnvilRegion(const AnvilRegion&) = delete;
    AnvilRegion(AnvilRegion&&) = delete;

    // Construct from the directory path, name of the file and region coordinates.
    AMULET_CORE_EXPORT AnvilRegion(const std::filesystem::path& directory, const std::string& file_name, std::int64_t rx, std::int64_t rz, bool mcc = false);

    // Construct from the directory path and region coordinates.
    // File name is computed from region coordinates.
    AMULET_CORE_EXPORT AnvilRegion(const std::filesystem::path& directory, std::int64_t rx, std::int64_t rz, bool mcc = false);

    // Construct from the path to the region file.
    // Coordinates are computed from the file name.
    // File name must match "r.X.Z.mca".
    AMULET_CORE_EXPORT AnvilRegion(std::filesystem::path path, bool mcc = false);

    // Destructor
    AMULET_CORE_EXPORT ~AnvilRegion();

    // Assignment operators
    AnvilRegion& operator=(const AnvilRegion&) = delete;
    AnvilRegion& operator=(AnvilRegion&&) = delete;

    // A mutex which can be used to synchronise calls.
    // Thread safe.
    AMULET_CORE_EXPORT Amulet::OrderedMutex& get_mutex();

    // The path of the region file.
    // Thread safe.
    AMULET_CORE_EXPORT std::filesystem::path path() const;

    // The region x coordinate of the file.
    // Thread safe.
    AMULET_CORE_EXPORT std::int64_t rx() const;

    // The region z coordinate of the file.
    // Thread safe.
    AMULET_CORE_EXPORT std::int64_t rz() const;

    // Get the coordinates of all values in the region file.
    // Coordinates are in world space.
    // External Read:SharedReadWrite lock required.
    // External Read:SharedReadOnly lock optional.
    AMULET_CORE_EXPORT std::vector<std::pair<std::int64_t, std::int64_t>> get_coords();

    // Is the coordinate in the region.
    // This returns true even if there is no value for the coordinate.
    // Coordinates are in world space.
    // Thread safe.
    AMULET_CORE_EXPORT bool contains(std::int64_t cx, std::int64_t cz) const;

    // Is there a value stored for this coordinate.
    // Coordinates are in world space.
    // External Read:SharedReadWrite lock required.
    // External Read:SharedReadOnly lock optional.
    AMULET_CORE_EXPORT bool has_value(std::int64_t cx, std::int64_t cz);

    // Get the value for this coordinate.
    // Coordinates are in world space.
    // External Read:SharedReadWrite lock required.
    AMULET_CORE_EXPORT AmuletNBT::NamedTag get_value(std::int64_t cx, std::int64_t cz);
    
    // AMULET_CORE_EXPORT std::vector<std::optional<AmuletNBT::NamedTag>> get_batch(std::vector<std::pair<std::int64_t, std::int64_t>>& coords);

    // Set the value for this coordinate.
    // Coordinates are in world space.
    // External ReadWrite:SharedReadWrite lock required.
    AMULET_CORE_EXPORT void set_value(std::int64_t cx, std::int64_t cz, const AmuletNBT::NamedTag& tag);
    
    // AMULET_CORE_EXPORT void set_batch(std::vector<std::tuple<std::int64_t, std::int64_t, AmuletNBT::NamedTag>>& batch);

    // Delete the chunk data.
    // Coordinates are in world space.
    // External ReadWrite:SharedReadWrite lock required.
    AMULET_CORE_EXPORT void delete_value(std::int64_t cx, std::int64_t cz);

    // Delete multiple chunk's data.
    // Coordinates are in world space.
    // External ReadWrite:SharedReadWrite lock required.
    AMULET_CORE_EXPORT void delete_batch(std::vector<std::pair<std::int64_t, std::int64_t>>& coords);

    // Compact the region file.
    // Defragments the file and deletes unused space.
    // If there are no chunks remaining in the region file it will be deleted.
    // External ReadWrite:SharedReadWrite lock required.
    AMULET_CORE_EXPORT void compact();

    // Close the file object if open.
    // This is automatically called when the instance is destroyed but may be called earlier.
    // Thread safe.
    AMULET_CORE_EXPORT void close();

    // Destroy the instance.
    // Calls made after this will fail.
    // This may only be called by the owner of the instance.
    // External ReadWrite:Unique lock required.
    AMULET_CORE_EXPORT void destroy();

    // Has the instance been destroyed.
    // If this is false, other calls will fail.
    // External Read:SharedReadWrite lock required.
    AMULET_CORE_EXPORT bool is_destroyed();

    // Get the object responsible for closing the region file.
    // When this object is deleted it will close the region file
    // This means that holding a reference to this will delay when the region file is closed.
    // The region file may still be closed manually before this object is deleted.
    // Thread safe.
    AMULET_CORE_EXPORT std::shared_ptr<FileCloser> get_file_closer();
};

class AMULET_CORE_EXPORT_EXCEPTION RegionDoesNotExist : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
    RegionDoesNotExist()
        : RegionDoesNotExist("RegionDoesNotExist")
    {
    }
};

} // namespace Amulet
