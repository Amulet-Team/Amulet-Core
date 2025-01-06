#pragma once
#include <cstdint>
#include <filesystem>
#include <memory>
#include <shared_mutex>
#include <string>
#include <vector>

#include <amulet/biome.hpp>
#include <amulet/block.hpp>
#include <amulet/chunk.hpp>
#include <amulet/version.hpp>
#include <amulet/utils/task_manager/cancel_manager.hpp>
#include <amulet/utils/task_manager/progress_manager.hpp>

namespace Amulet {

class ChunkHandle {
public:
    virtual ~ChunkHandle() { }
    virtual std::string dimension_id() = 0;
    virtual std::int64_t cx() = 0;
    virtual std::int64_t cz() = 0;
    virtual bool exists() = 0;
    virtual std::shared_ptr<Chunk> get_chunk() = 0;
    virtual void set_chunk(std::shared_ptr<Chunk>) = 0;
    virtual void delete_chunk() = 0;
};

class Dimension {
public:
    virtual ~Dimension() { }
    virtual std::string dimension_id() = 0;
    virtual const BlockStack& default_block() = 0;
    virtual const Biome& default_biome() = 0;
    virtual std::shared_ptr<ChunkHandle> get_chunk_handle(std::int64_t, std::int64_t) = 0;
};

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

class CompactibleLevel {
public:
    virtual ~CompactibleLevel() {};

    // Compact the level data to reduce file size.
    virtual void compact() = 0;
};

class DiskLevel {
public:
    virtual ~DiskLevel() {};

    // The path to the level on disk.
    virtual std::filesystem::path path() = 0;
};

class ReloadableLevel {
public:
    virtual ~ReloadableLevel() {};

    // Reload the metadata in the existing instance.
    // This can only be done when the level is not open.
    virtual void reload() = 0;
};

class LevelLoader {
public:
    class Token {
    public:
        virtual ~Token() { }
    };

    class PathToken : public Token {
    public:
        std::filesystem::path path;
        PathToken(std::filesystem::path path)
            : path(path)
        {
        }
    };

    virtual ~LevelLoader() {};

    // The name of the loader.
    virtual std::string name() const = 0;

    // Can the loader load the level token.
    virtual bool can_load(const Token&) const = 0;

    // Load the level from the token.
    virtual std::unique_ptr<Level> load(const Token&) const = 0;
};

} // namespace Amulet
