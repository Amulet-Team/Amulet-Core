#pragma once

#include <chrono>
#include <filesystem>
#include <map>
#include <memory>

#include <amulet/image/image.hpp>
#include <amulet/level/abc/dimension.hpp>
#include <amulet/level/abc/history.hpp>
#include <amulet/level/abc/level.hpp>

#include "raw_level.hpp"
#include "dimension.hpp"

namespace Amulet {

class JavaLevelOpenData {
public:
    HistoryManager history_manager;
    std::shared_ptr<bool> history_enabled;
    std::shared_mutex dimensions_mutex;
    std::map<DimensionID, std::shared_ptr<JavaDimension>> dimensions;

    JavaLevelOpenData();
};

class JavaLevel : public Level, public CompactibleLevel, public DiskLevel, public ReloadableLevel {
private:
    std::unique_ptr<JavaRawLevel> _raw_level;

    // Data that is only valid when the level is open.
    std::unique_ptr<JavaLevelOpenData> _open_data;

    // Validate _open_data is valid and return a reference.
    // External Read:SharedReadWrite lock required.
    JavaLevelOpenData& _get_open_data()
    {
        if (!_open_data) {
            throw std::runtime_error("The level is not open.");
        }
        return *_open_data;
    }

    JavaLevel(std::unique_ptr<JavaRawLevel>);

public:
    JavaLevel() = delete;
    JavaLevel(const JavaLevel&) = delete;
    JavaLevel& operator=(const JavaLevel&) = delete;
    JavaLevel(JavaLevel&&) = delete;
    JavaLevel& operator=(JavaLevel&&) = delete;

    ~JavaLevel();

    // Load an existing Java level from the given directory.
    // Thread safe.
    AMULET_CORE_EXPORT static std::unique_ptr<JavaLevel> load(const std::filesystem::path&);

    // Create a new Java level at the given directory.
    // Thread safe.
    AMULET_CORE_EXPORT static std::unique_ptr<JavaLevel> create(const JavaCreateArgsV1&);

    // LevelMetadata

    // Is the level open.
    // External Read:SharedReadWrite lock required.
    AMULET_CORE_EXPORT bool is_open() override;

    // The platform string for the level.
    // External Read:SharedReadWrite lock required.
    AMULET_CORE_EXPORT const std::string get_platform() override;

    // The maximum game version the level has been opened with.
    // External Read:SharedReadWrite lock required.
    AMULET_CORE_EXPORT const VersionNumber get_max_game_version() override;

    // Is this level a supported version.
    // This is true for all versions we support and false for snapshots and unsupported newer versions.
    // External Read:SharedReadWrite lock required.
    AMULET_CORE_EXPORT bool is_supported() override;

    // The thumbnail for the level.
    // External Read:SharedReadWrite lock required.
    PIL::Image::Image get_thumbnail() override;

    // The name of the level.
    // External Read:SharedReadWrite lock required.
    AMULET_CORE_EXPORT const std::string get_level_name() override;

    // The time when the level was last modified.
    // External Read:SharedReadWrite lock required.
    AMULET_CORE_EXPORT std::chrono::system_clock::time_point get_modified_time() override;

    // The size of the sub-chunk. Must be a cube.
    // External Read:SharedReadWrite lock required.
    AMULET_CORE_EXPORT size_t get_sub_chunk_size() override;

    // DiskLevel

    // The path to the level on disk.
    // External Read:SharedReadWrite lock required.
    AMULET_CORE_EXPORT const std::filesystem::path& get_path() override;

    // Level

    // Open the level.
    // If the level is already open, this does nothing.
    // External ReadWrite:Unique lock required.
    AMULET_CORE_EXPORT void open() override;

    // Clear all unsaved changes and restore points.
    // External ReadWrite:Unique lock required.
    AMULET_CORE_EXPORT void purge() override;

    // Save changes to the level.
    // External ReadWrite:Unique lock required.
    AMULET_CORE_EXPORT void save() override;

    // Close the level.
    // If the level is not open, this does nothing.
    // External ReadWrite:Unique lock required.
    AMULET_CORE_EXPORT void close() override;

    // Create a new history restore point.
    // Any changes made after this point can be reverted by calling undo.
    // External Read:SharedReadWrite lock required.
    void create_restore_point() override;

    // Get the number of times undo can be called.
    // External Read:SharedReadWrite lock required.
    // External Read:SharedReadOnly lock optional.
    size_t get_undo_count() override;

    // Revert the changes made since the previous restore point.
    // External ReadWrite:SharedReadWrite lock required.
    // External ReadWrite:Unique lock optional.
    void undo() override;

    // Get the number of times redo can be called.
    // External Read:SharedReadWrite lock required.
    // External Read:SharedReadOnly lock optional.
    size_t get_redo_count() override;

    // Redo changes that were previously reverted.
    // External ReadWrite:SharedReadWrite lock required.
    // External ReadWrite:Unique lock optional.
    void redo() override;

    // Get if the history system is enabled.
    // If this is true, the caller must call create_restore_point before making changes.
    // External Read:SharedReadWrite lock required.
    bool get_history_enabled() override;

    // Set if the history system is enabled.
    // External ReadWrite:SharedReadWrite lock required.
    void set_history_enabled(bool) override;

    // The identifiers for all dimensions in the level
    // External Read:SharedReadWrite lock required.
    // External Read:SharedReadOnly lock optional.
    AMULET_CORE_EXPORT std::vector<std::string> get_dimension_ids() override;

    // Get a dimension.
    // External Read:SharedReadWrite lock required.
    // External ReadWrite:SharedReadWrite lock required when calling code in Dimension (and its children) that need write permission.
    AMULET_CORE_EXPORT std::shared_ptr<JavaDimension> get_java_dimension(const DimensionID&);

    // Get a dimension.
    // External Read:SharedReadWrite lock required.
    // External ReadWrite:SharedReadWrite lock required when calling code in Dimension (and its children) that need write permission.
    AMULET_CORE_EXPORT std::shared_ptr<Dimension> get_dimension(const DimensionID&) override;

    // CompactibleLevel

    // Compact the level data to reduce file size.
    // External ReadWrite:SharedReadWrite lock required.
    AMULET_CORE_EXPORT void compact() override;

    // ReloadableLevel

    // Reload the level metadata.
    // This can only be done when the level is not open.
    // External ReadWrite:Unique lock required.
    AMULET_CORE_EXPORT void reload_metadata() override;

    // Reload the level.
    // This is like closing and opening the level but does not release locks.
    // This can only be done when the level is open.
    // External ReadWrite:Unique lock required.
    AMULET_CORE_EXPORT void reload() override;

    // Access the raw level instance.
    // Before calling any mutating functions, the caller must call `purge` (optionally saving before)
    // External ReadWrite:Unique lock required.
    AMULET_CORE_EXPORT JavaRawLevel& get_raw_level();
};

} // namespace Amulet
