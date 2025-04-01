#pragma once

#include <memory>
#include <shared_mutex>
#include <variant>

#include "chunk_handle.hpp"
#include "raw_dimension.hpp"
#include <amulet/dll.hpp>
#include <amulet/level/abc/chunk_handle.hpp>
#include <amulet/level/abc/dimension.hpp>
#include <amulet/level/abc/history.hpp>

namespace Amulet {

class JavaDimension : public Dimension {
private:
    std::map<std::pair<std::int64_t, std::int64_t>, std::weak_ptr<JavaChunkHandle>> _chunk_handles;
    std::shared_mutex _chunk_handles_mutex;

    std::shared_ptr<JavaRawDimension> _raw_dimension;

    std::shared_ptr<HistoryManagerLayer<detail::ChunkKey>> _chunk_history;
    std::shared_ptr<HistoryManagerLayer<std::string>> _chunk_data_history;

    std::shared_ptr<bool> _history_enabled;

    JavaDimension(
        std::shared_ptr<JavaRawDimension> raw_dimension,
        HistoryManager& history_manager,
        std::shared_ptr<bool> history_enabled);

    friend class JavaLevel;

public:
    // Destructor
    AMULET_CORE_EXPORT ~JavaDimension() override;

    // Get the dimension id for this dimension.
    // Thread safe.
    AMULET_CORE_EXPORT const DimensionID& get_dimension_id() const override;

    // The editable region of the dimension.
    // Thread safe.
    AMULET_CORE_EXPORT std::variant<SelectionBox, SelectionGroup> get_bounds() const override;

    // Get the default block for this dimension.
    // Thread safe.
    AMULET_CORE_EXPORT const BlockStack& get_default_block() const override;

    // Get the default biome for this dimension.
    // Thread safe.
    AMULET_CORE_EXPORT const Biome& get_default_biome() const override;

    // Get a chunk handle for a specific chunk.
    // Thread safe.
    AMULET_CORE_EXPORT std::shared_ptr<JavaChunkHandle> get_java_chunk_handle(std::int64_t cx, std::int64_t cz);

    // Get a chunk handle for a specific chunk.
    // Thread safe.
    AMULET_CORE_EXPORT std::shared_ptr<ChunkHandle> get_chunk_handle(std::int64_t cx, std::int64_t cz) override;
};

} // namespace Amulet
