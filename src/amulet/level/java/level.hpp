#pragma once

#include <chrono>
#include <filesystem>

#include <amulet/level/abc/level.hpp>

#include "raw_level.hpp"

namespace Amulet {

class JavaLevelOpenData {

};

class JavaLevel : public Level, public CompactibleLevel, public DiskLevel, public ReloadableLevel {
private:
    std::unique_ptr<JavaRawLevel> _raw_level;

    JavaLevel(std::unique_ptr<JavaRawLevel>);

public:
    JavaLevel() = delete;
    JavaLevel(const JavaLevel&) = delete;
    JavaLevel& operator=(const JavaLevel&) = delete;
    JavaLevel(JavaLevel&&) = delete;
    JavaLevel& operator=(JavaLevel&&) = delete;

    // Load an existing Java level from the given directory.
    // Thread safe.
    AMULET_CORE_EXPORT static std::unique_ptr<JavaLevel> load(const std::filesystem::path&);

    // Create a new Java level at the given directory.
    // Thread safe.
    AMULET_CORE_EXPORT static std::unique_ptr<JavaLevel> create(const JavaCreateArgsV1&);

    // LevelMetadata

    // Is the level open.
    AMULET_CORE_EXPORT bool is_open() override;

    // The platform string for the level.
    AMULET_CORE_EXPORT const std::string get_platform() override;

    // The maximum game version the level has been opened with.
    AMULET_CORE_EXPORT const VersionNumber get_max_game_version() override;

    // The thumbnail for the level.
    // void thumbnail() override;

    // The name of the level.
    AMULET_CORE_EXPORT const std::string get_level_name() override;

    // The time when the level was last modified.
    AMULET_CORE_EXPORT std::chrono::system_clock::time_point get_modified_time() override;

    // The size of the sub-chunk. Must be a cube.
    AMULET_CORE_EXPORT size_t get_sub_chunk_size() override;

    // Level

    // Open the level for editing.
    // If the level is already open, this does nothing.
    AMULET_CORE_EXPORT void open() override;

    // Unload all loaded data.
    //AMULET_CORE_EXPORT void purge() override;

    // Save changes to the level.
    AMULET_CORE_EXPORT void save() override;

    // Close the level.
    AMULET_CORE_EXPORT void close() override;

    // size_t undo_count() override;
    // void undo() override;
    // size_t redo_count() override;
    // void redo() override;
    // bool is_history_enabled() override;
    // void set_history_enabled(bool) override;

    // The identifiers for all dimensions in the level
    AMULET_CORE_EXPORT std::vector<std::string> get_dimension_ids() override;

    // Get a dimension.
    AMULET_CORE_EXPORT std::shared_ptr<Dimension> get_dimension(const std::string&) override;

    // CompactibleLevel

    // Compact the level data to reduce file size.
    AMULET_CORE_EXPORT void compact() override;

    // DiskLevel

    // The path to the level on disk.
    AMULET_CORE_EXPORT const std::filesystem::path& get_path() override;

    // ReloadableLevel

    // Reload the level metadata.
    // This can only be done when the level is not open.
    AMULET_CORE_EXPORT void reload_metadata() override;
    
    // Reload the level.
    // This is like closing and opening the level but does not release locks.
    // This can only be done when the level is open.
    AMULET_CORE_EXPORT void reload() override;
};

} // namespace Amulet
