#pragma once

#include <memory>
#include <shared_mutex>
#include <string>
#include <vector>

#include <amulet/version.hpp>

#include "dimension.hpp"

namespace Amulet {

// Functions that can be accessed while the level is closed.
class LevelMetadata {
private:
    std::shared_mutex _mutex;

public:
    virtual ~LevelMetadata() = default;

    // Is the level open.
    virtual void is_open() = 0;

    // The platform string for the level.
    virtual const std::string& platform() = 0;

    // The maximum game version the leve has been opened with.
    virtual const VersionNumber& max_game_version() = 0;

    // The thumbnail for the level.
    // virtual void thumbnail() = 0;

    // The name of the level.
    virtual std::string level_name() = 0;

    // The time the level was modified (Unix time in seconds) or 0 if unknown.
    virtual double modified_time() = 0;

    // The size of the sub-chunk. Must be a cube.
    virtual size_t sub_chunk_size() = 0;

    std::shared_mutex& mutex() { return _mutex; }
};

class Level : public LevelMetadata {
public:
    // Open the level for editing.
    // If the level is already open, this does nothing.
    virtual void open() = 0;

    // Unload all loaded data.
    virtual void purge() = 0;

    // Save changes to the level.
    virtual void save() = 0;

    // Close the level.
    virtual void close() = 0;

    // virtual size_t undo_count() = 0;
    // virtual void undo() = 0;
    // virtual size_t redo_count() = 0;
    // virtual void redo() = 0;
    // virtual bool is_history_enabled() = 0;
    // virtual void set_history_enabled(bool) = 0;

    // The identifiers for all dimensions in the level
    virtual std::vector<std::string> dimension_ids() = 0;

    // Get a dimension.
    virtual std::shared_ptr<Dimension> get_dimension(const std::string&) = 0;
};

} // namespace Amulet
