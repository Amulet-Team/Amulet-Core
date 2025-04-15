#pragma once

#include <chrono>
#include <memory>
#include <shared_mutex>
#include <string>
#include <vector>

#include <amulet/image/image.hpp>
#include <amulet/utils/mutex.hpp>
#include <amulet/utils/signal.hpp>
#include <amulet/version/version.hpp>

#include "dimension.hpp"

namespace Amulet {

// Functions that can be accessed while the level is closed.
class LevelMetadata {
protected:
    OrderedMutex _mutex;

public:
    virtual ~LevelMetadata() = default;

    // The external mutex for the level.
    // Thread safe.
    OrderedMutex& get_mutex() { return _mutex; }

    // Is the level open.
    // External Read:SharedReadWrite lock required.
    virtual bool is_open() = 0;

    // The platform string for the level.
    // External Read:SharedReadWrite lock required.
    virtual const std::string get_platform() = 0;

    // The maximum game version the level has been opened with.
    // External Read:SharedReadWrite lock required.
    virtual const VersionNumber get_max_game_version() = 0;

    // Is this level a supported version.
    // This is true for all versions we support and false for snapshots, betas and unsupported newer versions.
    // External Read:SharedReadWrite lock required.
    virtual bool is_supported() = 0;

    // The thumbnail for the level.
    // External Read:SharedReadWrite lock required.
    virtual PIL::Image::Image get_thumbnail() = 0;

    // The name of the level.
    // External Read:SharedReadWrite lock required.
    virtual const std::string get_level_name() = 0;

    // The time when the level was last modified.
    // External Read:SharedReadWrite lock required.
    virtual std::chrono::system_clock::time_point get_modified_time() = 0;

    // The size of the sub-chunk. Must be a cube.
    // External Read:SharedReadWrite lock required.
    virtual size_t get_sub_chunk_size() = 0;
};

class Level : public LevelMetadata {
public:
    // Signal emitted when the level is opened.
    // Thread safe.
    Signal<> opened;

    // Open the level.
    // If the level is already open, this does nothing.
    // External ReadWrite:Unique lock required.
    virtual void open() = 0;

    // Signal emitted when the level is purged
    // Thread safe.
    Signal<> purged;

    // Clear all unsaved changes and restore points.
    // External ReadWrite:Unique lock required.
    virtual void purge() = 0;

    // Save all changes to the level.
    // External ReadWrite:Unique lock required.
    virtual void save() = 0;

    // Signal emitted when the level is closed
    // Thread safe.
    Signal<> closed;

    // Close the level.
    // If the level is not open, this does nothing.
    // External ReadWrite:Unique lock required.
    virtual void close() = 0;

    // A signal emitted when the undo or redo count changes.
    // Thread safe.
    Signal<> history_changed;

    // Create a new history restore point.
    // Any changes made after this point can be reverted by calling undo.
    // External Read:SharedReadWrite lock required.
    virtual void create_restore_point() = 0;

    // Get the number of times undo can be called.
    // External Read:SharedReadWrite lock required.
    // External Read:SharedReadOnly lock optional.
    virtual size_t get_undo_count() = 0;

    // Revert the changes made since the previous restore point.
    // External ReadWrite:SharedReadWrite lock required.
    // External ReadWrite:Unique lock optional.
    virtual void undo() = 0;

    // Get the number of times redo can be called.
    // External Read:SharedReadWrite lock required.
    // External Read:SharedReadOnly lock optional.
    virtual size_t get_redo_count() = 0;

    // Redo changes that were previously reverted.
    // External ReadWrite:SharedReadWrite lock required.
    // External ReadWrite:Unique lock optional.
    virtual void redo() = 0;

    // A signal emitted when set_history_enabled is called.
    // Thread safe.
    Signal<> history_enabled_changed;

    // Get if the history system is enabled.
    // If this is true, the caller must call create_restore_point before making changes.
    // External Read:SharedReadWrite lock required.
    virtual bool get_history_enabled() = 0;

    // Set if the history system is enabled.
    // External ReadWrite:SharedReadWrite lock required.
    virtual void set_history_enabled(bool) = 0;

    // The identifiers for all dimensions in the level
    // External Read:SharedReadWrite lock required.
    // External Read:SharedReadOnly lock optional.
    virtual std::vector<std::string> get_dimension_ids() = 0;

    // Get a dimension.
    // External Read:SharedReadWrite lock required.
    // External ReadWrite:SharedReadWrite lock required when calling code in Dimension (and its children) that need write permission.
    virtual std::shared_ptr<Dimension> get_dimension(const std::string&) = 0;
};

class CompactibleLevel {
public:
    virtual ~CompactibleLevel() = default;

    // Compact the level data to reduce file size.
    // External ReadWrite:SharedReadWrite lock required.
    virtual void compact() = 0;
};

class DiskLevel {
public:
    virtual ~DiskLevel() = default;

    // The path to the level on disk.
    // External Read:SharedReadWrite lock required.
    virtual const std::filesystem::path& get_path() = 0;
};

class ReloadableLevel {
public:
    virtual ~ReloadableLevel() = default;

    // Reload the level metadata.
    // This can only be done when the level is not open.
    // External ReadWrite:Unique lock required.
    virtual void reload_metadata() = 0;

    // Signal emitted when the level is reloaded.
    // Thread safe.
    Signal<> reloaded;

    // Reload the level.
    // This is like closing and opening the level but does not release locks.
    // This can only be done when the level is open.
    // External ReadWrite:Unique lock required.
    virtual void reload() = 0;
};

} // namespace Amulet
