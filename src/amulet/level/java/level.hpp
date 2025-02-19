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
    std::shared_ptr<JavaRawLevel> _raw_level;

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
    AMULET_CORE_EXPORT virtual bool is_open() override;

    // The platform string for the level.
    AMULET_CORE_EXPORT virtual const std::string get_platform() override;

    // The maximum game version the level has been opened with.
    AMULET_CORE_EXPORT virtual const VersionNumber get_max_game_version() override;

    // The thumbnail for the level.
    // virtual void thumbnail() override;

    // The name of the level.
    AMULET_CORE_EXPORT virtual const std::string get_level_name() override;

    // The time when the level was last modified.
    AMULET_CORE_EXPORT virtual std::chrono::system_clock::time_point get_modified_time() override;

    // The size of the sub-chunk. Must be a cube.
    AMULET_CORE_EXPORT virtual size_t get_sub_chunk_size() override;

    // Level

    // Open the level for editing.
    // If the level is already open, this does nothing.
    AMULET_CORE_EXPORT virtual void open() override;

    // Unload all loaded data.
    AMULET_CORE_EXPORT virtual void purge() override;

    // Save changes to the level.
    AMULET_CORE_EXPORT virtual void save() override;

    // Close the level.
    AMULET_CORE_EXPORT virtual void close() override;

    // virtual size_t undo_count() override;
    // virtual void undo() override;
    // virtual size_t redo_count() override;
    // virtual void redo() override;
    // virtual bool is_history_enabled() override;
    // virtual void set_history_enabled(bool) override;

    // The identifiers for all dimensions in the level
    AMULET_CORE_EXPORT virtual std::vector<std::string> get_dimension_ids() override;

    // Get a dimension.
    AMULET_CORE_EXPORT virtual std::shared_ptr<Dimension> get_dimension(const std::string&) override;

    // CompactibleLevel

    AMULET_CORE_EXPORT virtual void compact() override;

    // DiskLevel

    AMULET_CORE_EXPORT virtual const std::filesystem::path& get_path() override;

    // ReloadableLevel

    // AMULET_CORE_EXPORT void reload() override;
    AMULET_CORE_EXPORT virtual void reload_metadata() override;
};

} // namespace Amulet
