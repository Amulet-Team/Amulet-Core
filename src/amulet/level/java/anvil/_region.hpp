#include <cstdint>
#include <filesystem>
#include <map>
#include <mutex>
#include <optional>
#include <string>

#include <amulet/dll.hpp>
#include <amulet_nbt/tag/named_tag.hpp>

#include "_sector_manager.hpp"

namespace Amulet {

AMULET_CORE_DLLX std::pair<std::int64_t, std::int64_t> parse_region_filename(const std::string& filename);

// A class to read and write Minecraft Java Edition Region files.
// Only one instance should exist per region file at any given time otherwise bad things may happen.
class AnvilRegion {
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

    // This mutex must be acquired to access the container data or the file.
    std::mutex mutex;

    AnvilRegion(const std::filesystem::path& directory, const std::string& file_name, const std::pair<std::int64_t, std::int64_t>& region_coordinate, bool mcc = false);

    // Load data from the region file if it exists.
    // Must be called with the lock.
    void load();

    void validate_coord(std::int64_t cx, std::int64_t cz);
    template <typename T>
    void _set_data(std::int64_t cx, std::int64_t cz, T data);

public:
    // Constructors.
    AMULET_CORE_DLLX AnvilRegion(const std::filesystem::path& directory, const std::string& file_name, std::int64_t rx, std::int64_t rz, bool mcc = false);
    AMULET_CORE_DLLX AnvilRegion(const std::filesystem::path& directory, std::int64_t rx, std::int64_t rz, bool mcc = false);
    AMULET_CORE_DLLX AnvilRegion(std::filesystem::path path, bool mcc = false);

    // The path of the region file.
    AMULET_CORE_DLLX std::filesystem::path path() const;

    // The region coordinates of the file.
    AMULET_CORE_DLLX std::int64_t rx() const;
    AMULET_CORE_DLLX std::int64_t rz() const;

    //
    AMULET_CORE_DLLX void all_coords();

    // Does the chunk exists. Coords are in world space.
    AMULET_CORE_DLLX bool has_data(std::int64_t cx, std::int64_t cz);

    // Get the data for the chunk. Coords are in world space.
    AMULET_CORE_DLLX AmuletNBT::NamedTag get_data(std::int64_t cx, std::int64_t cz);

    // Set the data for the chunk. Coords are in world space.
    AMULET_CORE_DLLX void set_data(std::int64_t cx, std::int64_t cz, const AmuletNBT::NamedTag& tag);

    // Delete the chunk data. Coords are in world space.
    AMULET_CORE_DLLX void delete_data(std::int64_t cx, std::int64_t cz);

    // Compact the region file.
    // Defragments the file and deletes unused space.
    // If there are no chunks remaining in the region file it will be deleted.
    AMULET_CORE_DLLX void compact();
};

} // namespace Amulet
