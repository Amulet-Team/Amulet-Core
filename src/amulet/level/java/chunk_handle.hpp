#pragma once

#include <amulet/dll.hpp>

#include <amulet/level/abc/chunk_handle.hpp>

#include "chunk.hpp"

namespace Amulet {

class JavaChunkHandle : public ChunkHandle {
private:
    JavaChunkHandle(
        const DimensionID& dimension_id,
        std::int64_t cx,
        std::int64_t cz)
        : ChunkHandle(dimension_id, cx, cz)
    {
    }

    friend class JavaDimension;

public:
    // Does the chunk exist. This is a quick way to check if the chunk exists without loading it.
    AMULET_CORE_EXPORT bool exists() override;

    // Get a unique copy of the chunk data.
    AMULET_CORE_EXPORT std::unique_ptr<Chunk> get_chunk() override;

    // Overwrite the chunk data.
    AMULET_CORE_EXPORT void set_chunk(const Chunk&) override;

    // Delete the chunk from the level.
    AMULET_CORE_EXPORT void delete_chunk() override;
};

} // namespace Amulet
