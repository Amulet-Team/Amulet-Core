#pragma once

#include <chrono>
#include <filesystem>
#include <map>
#include <memory>
#include <shared_mutex>
#include <stdexcept>

#include <amulet_nbt/tag/named_tag.hpp>

#include <amulet/dll.hpp>
#include <amulet/level/abc/registry.hpp>
#include <amulet/utils/mutex.hpp>
#include <amulet/version.hpp>

#include "dimension.hpp"
#include "raw_dimension.hpp"

namespace Amulet {

struct JavaCreateArgsV1 {
    bool overwrite;
    std::filesystem::path path;
    VersionNumber version;
    std::string level_name;
};

class JavaRawLevelOpenData {
public:
    // TODO: lock_file
    // TODO: lock_time
    // TODO: data_pack
    std::shared_mutex dimensions_mutex;
    std::map<JavaInternalDimensionID, std::shared_ptr<JavaRawDimension>> dimensions;
    std::map<DimensionID, JavaInternalDimensionID> dimension_ids;
    std::shared_ptr<IdRegistry> block_id_override;
    std::shared_ptr<IdRegistry> biome_id_override;
};

class JavaRawLevel {
private:
    OrderedMutex _public_mutex;
    std::filesystem::path _path;
    AmuletNBT::NamedTag _level_dat;
    VersionNumber _data_version;

    // Data that is only valid when the level is open.
    // The external unique lock must be held to change this pointer.
    std::unique_ptr<JavaRawLevelOpenData> _raw_open_data;

    // Construct a new instance. Path is the directory containing the level.dat file.
    JavaRawLevel(const std::filesystem::path path)
        : _path(path)
        , _level_dat("", std::make_shared<AmuletNBT::CompoundTag>())
        , _data_version({})
    {
    }

    // Validate _raw_open_data is valid and return a reference.
    // External shared read lock required.
    JavaRawLevelOpenData& _get_raw_open()
    {
        if (!_raw_open_data) {
            throw std::runtime_error("The level is not open.");
        }
        return *_raw_open_data;
    }

    JavaRawLevelOpenData& _find_dimensions();

public:
    JavaRawLevel() = delete;
    JavaRawLevel(const JavaRawLevel&) = delete;
    JavaRawLevel(JavaRawLevel&&) = default;

    // Create a new JavaRawLevel instance from the data at the path.
    AMULET_CORE_EXPORT static std::unique_ptr<JavaRawLevel> load(const std::filesystem::path&);

    // Create a new Java level and create a JavaRawLevel instance for it.
    AMULET_CORE_EXPORT static std::unique_ptr<JavaRawLevel> create(const JavaCreateArgsV1&);

    // External mutex
    // Thread safe.
    AMULET_CORE_EXPORT OrderedMutex& mutex();

    // Is the level open.
    // External shared read lock required.
    AMULET_CORE_EXPORT bool is_open() const;

    // Reload the metadata. This can only be called when the level is closed.
    // External unique lock required.
    AMULET_CORE_EXPORT void reload_metadata();

    // Open the level.
    // External unique lock required.
    AMULET_CORE_EXPORT void open();

    // Close the level.
    // External unique lock required.
    AMULET_CORE_EXPORT void close();

    // The path to the level directory.
    // Thread safe.
    AMULET_CORE_EXPORT const std::filesystem::path& get_path() const;

    // The NamedTag stored in the level.dat file. Returns a unique copy.
    // External shared read lock required.
    AMULET_CORE_EXPORT AmuletNBT::NamedTag get_level_dat() const;

    // Set the level.dat NamedTag
    // External unique lock required.
    AMULET_CORE_EXPORT void set_level_dat(const AmuletNBT::NamedTag&);

    // The platform identifier. "java"
    // Thread safe.
    AMULET_CORE_EXPORT std::string get_platform() const;

    // The game data version that the level was last opened in.
    // External shared read lock required.
    const VersionNumber& get_data_version() const;

    // Set the maximum game version.
    // If the game version is different this will close and re-open the level.
    // External unique lock required.
    void set_data_version();

    // The time when the level was lasted edited.
    AMULET_CORE_EXPORT std::chrono::system_clock::time_point modified_time() const;

    // The name of the level.
    AMULET_CORE_EXPORT std::string level_name() const;

    // Set the level name.
    AMULET_CORE_EXPORT void set_level_name(const std::string&);

    // The identifiers for all dimensions in this level.
    // External shared read lock required.
    // External shared read-only lock optional.
    AMULET_CORE_EXPORT std::vector<std::string> get_dimension_ids();

    // Get the raw dimension object for a specific dimension.
    // External shared read lock required.
    AMULET_CORE_EXPORT std::shared_ptr<JavaRawDimension> get_dimension(const DimensionID&);

    // Compact the level.
    // Thread safe.
    AMULET_CORE_EXPORT void compact();

    // Overridden block ids.
    // External shared read lock required.
    AMULET_CORE_EXPORT std::shared_ptr<IdRegistry> get_block_id_override();

    // Overridden biome ids.
    // External shared read lock required.
    AMULET_CORE_EXPORT std::shared_ptr<IdRegistry> get_biome_id_override();
};

} // namespace Amulet
