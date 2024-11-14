#include <cstdint>
#include <filesystem>
#include <map>
#include <optional>
#include <mutex>
#include <string>

#include <amulet_nbt/tag/named_tag.hpp>

#include "_sector_manager.hpp"

namespace Amulet {

std::pair<std::int64_t, std::int64_t> parse_region_filename(const std::string& filename);

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

    // This mutex must be aquired access the container data or the file.
    std::mutex mutex;

    AnvilRegion(const std::filesystem::path& directory, const std::string& file_name, const std::pair<std::int64_t, std::int64_t>& region_coordinate, bool mcc = false);
    
    // Load data from the region file if it exists.
    // Must be called with the lock.
    void load();

public:
    // Constructors.
    AnvilRegion(const std::filesystem::path& directory, const std::string& file_name, std::int64_t rx, std::int64_t rz, bool mcc = false);
    AnvilRegion(const std::filesystem::path& directory, std::int64_t rx, std::int64_t rz, bool mcc = false);
    AnvilRegion(std::filesystem::path path, bool mcc = false);
    
    // The path of the region file.
    std::filesystem::path path() const;
    
    // The region coordinates of the file.
    std::int64_t rx() const;
    std::int64_t rz() const;

    //
    void all_coords();
    
    // Does the chunk exists. Coords are in world space.
    bool has_data(std::uint8_t cx, std::uint8_t cz);
    
    // Get the data for the chunk. Coords are in world space.
    AmuletNBT::NamedTag get_data(std::uint8_t cx, std::uint8_t cz);

    // Set the data for the chunk. Coords are in world space.
    void set_data(std::uint8_t cx, std::uint8_t cz, const AmuletNBT::NamedTag& tag);

    // Delete the chunk data. Coords are in world space.
    void delete_data(std::uint8_t cx, std::uint8_t cz);
    
    // Compact the region file.
    // Defragments the file and deletes unused space.
    // If there are no chunks remaining in the region file it will be deleted.
    void compact();
};

} // namespace Amulet
