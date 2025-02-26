#pragma once

#include <chrono>
#include <memory>
#include <shared_mutex>
#include <string>
#include <vector>

#include <amulet/utils/mutex.hpp>
#include <amulet/version.hpp>
#include <amulet/utils/signal.hpp>

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
    // External shared read lock required.
    virtual bool is_open() = 0;

    // The platform string for the level.
    // External shared read lock required.
    virtual const std::string get_platform() = 0;

    // The maximum game version the level has been opened with.
    // External shared read lock required.
    virtual const VersionNumber get_max_game_version() = 0;

    // The thumbnail for the level.
    // virtual void thumbnail() = 0;

    // The name of the level.
    // External shared read lock required.
    virtual const std::string get_level_name() = 0;

    // The time when the level was last modified.
    // External shared read lock required.
    virtual std::chrono::system_clock::time_point get_modified_time() = 0;

    // The size of the sub-chunk. Must be a cube.
    // External shared read lock required.
    virtual size_t get_sub_chunk_size() = 0;
};

class Level : public LevelMetadata {
public:
    // Signal emitted when the level is opened.
    // Thread safe.
    Signal<> opened;

    // Open the level for editing.
    // If the level is already open, this does nothing.
    // External unique lock required.
    virtual void open() = 0;

    // Signal emitted when the level is purged
    // Thread safe.
    //Signal<> purged;

    // Clear all unsaved changes.
    // External unique lock required.
    //virtual void purge() = 0;

    // Save all changes to the level.
    // External unique lock required.
    virtual void save() = 0;

    // Signal emitted when the level is closed
    // Thread safe.
    Signal<> closed;

    // Close the level.
    // External unique lock required.
    virtual void close() = 0;

    // Signal<> history_changed;
    // virtual size_t undo_count() = 0;
    // virtual void undo() = 0;
    // virtual size_t redo_count() = 0;
    // virtual void redo() = 0;
    // virtual bool is_history_enabled() = 0;
    // virtual void set_history_enabled(bool) = 0;

    // The identifiers for all dimensions in the level
    // External shared read lock required.
    virtual std::vector<std::string> get_dimension_ids() = 0;

    // Get a dimension.
    // External shared read lock required.
    virtual std::shared_ptr<Dimension> get_dimension(const std::string&) = 0;
};

class CompactibleLevel {
public:
    virtual ~CompactibleLevel() = default;

    // Compact the level data to reduce file size.
    // External unique lock required.
    virtual void compact() = 0;
};

class DiskLevel {
public:
    virtual ~DiskLevel() = default;

    // The path to the level on disk.
    // External shared read lock required.
    virtual const std::filesystem::path& get_path() = 0;
};

class ReloadableLevel {
public:
    virtual ~ReloadableLevel() = default;

    // Reload the level metadata.
    // This can only be done when the level is not open.
    // External unique mutex required.
    virtual void reload_metadata() = 0;

    // Signal emitted when the level is reloaded.
    // Thread safe.
    Signal<> reloaded;

    // Reload the level.
    // This is like closing and opening the level but does not release locks.
    // This can only be done when the level is open.
    // External unique mutex required.
    virtual void reload() = 0;
};

} // namespace Amulet
