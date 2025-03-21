#pragma once

#include <amulet/dll.hpp>
#include <amulet/level/abc/chunk_handle.hpp>

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
    AMULET_CORE_EXPORT bool exists() override;
    AMULET_CORE_EXPORT std::shared_ptr<Chunk> get_chunk() override;
    AMULET_CORE_EXPORT void set_chunk(std::shared_ptr<Chunk>) override;
    AMULET_CORE_EXPORT void delete_chunk() override;
};

} // namespace Amulet
