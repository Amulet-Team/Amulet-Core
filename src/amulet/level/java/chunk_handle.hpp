#pragma once

#include <amulet/dll.hpp>

#include <amulet/level/abc/chunk_handle.hpp>
#include <amulet/level/abc/history.hpp>

#include "chunk.hpp"
#include "raw_dimension.hpp"

namespace Amulet {

class JavaChunkHandle : public ChunkHandle {
private:
    std::shared_ptr<HistoryManagerLayer<detail::ChunkKey>> _chunk_history;
    std::shared_ptr<HistoryManagerLayer<std::string>> _chunk_data_history;

    std::shared_ptr<JavaRawDimension> _raw_dimension;

    JavaChunkHandle(
        const DimensionID& dimension_id,
        std::int64_t cx,
        std::int64_t cz,
        std::shared_ptr<JavaRawDimension> raw_dimension,
        std::shared_ptr<HistoryManagerLayer<detail::ChunkKey>> chunk_history,
        std::shared_ptr<HistoryManagerLayer<std::string>> chunk_data_history);

    friend class JavaDimension;

public:
    // Does the chunk exist. This is a quick way to check if the chunk exists without loading it.
    AMULET_CORE_EXPORT bool exists() override;

    // Get a unique copy of the chunk data.
    AMULET_CORE_EXPORT std::unique_ptr<JavaChunk> get_java_chunk();

    // Get a unique copy of the chunk data.
    AMULET_CORE_EXPORT std::unique_ptr<Chunk> get_chunk() override;

    // Overwrite the chunk data.
    AMULET_CORE_EXPORT void set_java_chunk(const JavaChunk&);

    // Overwrite the chunk data.
    AMULET_CORE_EXPORT void set_chunk(const Chunk&) override;

    // Delete the chunk from the level.
    AMULET_CORE_EXPORT void delete_chunk() override;
};

} // namespace Amulet
