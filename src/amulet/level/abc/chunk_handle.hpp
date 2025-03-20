#pragma once

#include <cstdint>
#include <memory>
#include <string>

#include <amulet/chunk.hpp>
#include <amulet/utils/mutex.hpp>

namespace Amulet {

using DimensionID = std::string;

class ChunkHandle {
private:
    OrderedMutex _public_mutex;
    std::string _dimension_id;
    std::int64_t _cx;
    std::int64_t _cz;

protected:
    ChunkHandle(const DimensionID& dimension_id, std::int64_t cx, std::int64_t cz);

public:
    virtual ~ChunkHandle() = default;

    // The public mutex.
    // Thread safe.
    AMULET_CORE_EXPORT OrderedMutex& get_mutex();

    // The dimension identifier this chunk is from.
    // Thread safe.
    AMULET_CORE_EXPORT const std::string& get_dimension_id() const;

    // Get the chunk x coordinate.
    // Thread safe.
    AMULET_CORE_EXPORT std::int64_t get_cx() const;

    // Get the chunk z coordinate.
    // Thread safe.
    AMULET_CORE_EXPORT std::int64_t get_cz() const;

    // Does the chunk exist. This is a quick way to check if the chunk exists without loading it.
    virtual bool exists() = 0;

    // Get a unique copy of the chunk data.
    virtual std::shared_ptr<Chunk> get_chunk() = 0;

    // Overwrite the chunk data.
    virtual void set_chunk(std::shared_ptr<Chunk>) = 0;

    // Delete the chunk from the level.
    virtual void delete_chunk() = 0;
};

} // namespace Amulet
