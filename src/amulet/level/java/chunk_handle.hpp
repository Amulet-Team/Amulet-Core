#pragma once

#include <memory>

#include <amulet/dll.hpp>

#include <amulet/level/abc/chunk_handle.hpp>
#include <amulet/level/abc/history.hpp>

#include "chunk.hpp"
#include "raw_dimension.hpp"

namespace Amulet {

class JavaChunkHandle : public ChunkHandle {
private:
    std::shared_ptr<JavaRawDimension> _raw_dimension;

    std::shared_ptr<HistoryManagerLayer<detail::ChunkKey>> _chunk_history;
    std::shared_ptr<HistoryManagerLayer<std::string>> _chunk_data_history;

    std::shared_ptr<bool> _history_enabled;

    JavaChunkHandle(
        const DimensionID& dimension_id,
        std::int64_t cx,
        std::int64_t cz,
        std::shared_ptr<JavaRawDimension> raw_dimension,
        std::shared_ptr<HistoryManagerLayer<detail::ChunkKey>> chunk_history,
        std::shared_ptr<HistoryManagerLayer<std::string>> chunk_data_history,
        std::shared_ptr<bool> history_enabled);

    friend class JavaDimension;

    // Get the chunk instance will all components in their null state.
    // Requires _chunk_history shared lock.
    std::unique_ptr<JavaChunk> _get_null_chunk();

    // Load the chunk from the raw level.
    // Requires _chunk_history unique lock.
    void _preload();

public:
    // Does the chunk exist. This is a quick way to check if the chunk exists without loading it.
    AMULET_CORE_EXPORT bool exists() override;

    // Get a unique copy of the chunk data.
    AMULET_CORE_EXPORT std::unique_ptr<JavaChunk> get_java_chunk(std::optional<std::set<std::string>> component_ids = std::nullopt);

    // Get a unique copy of the chunk data.
    AMULET_CORE_EXPORT std::unique_ptr<Chunk> get_chunk(std::optional<std::set<std::string>> component_ids = std::nullopt) override;

    // Overwrite the chunk data.
    AMULET_CORE_EXPORT void set_java_chunk(const JavaChunk&);

    // Overwrite the chunk data.
    AMULET_CORE_EXPORT void set_chunk(const Chunk&) override;

    // Delete the chunk from the level.
    AMULET_CORE_EXPORT void delete_chunk() override;
};

} // namespace Amulet
