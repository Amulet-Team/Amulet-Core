#pragma once

#include <memory>

#include <amulet/dll.hpp>
#include <amulet/level/abc/dimension.hpp>
#include <amulet/level/abc/history.hpp>
#include "chunk_handle.hpp"
#include "raw_dimension.hpp"

namespace Amulet {

class JavaDimension : public Dimension {
private:
    std::map<std::pair<std::int64_t, std::int64_t>, std::weak_ptr<JavaChunkHandle>> _chunk_handles;
    std::shared_ptr<JavaRawDimension> _raw_dimension;
    //HistoryManagerLayer _chunk_history;
    //HistoryManagerLayer _chunk_data_history;

    JavaDimension(
        std::shared_ptr<JavaRawDimension> raw_dimension,
        HistoryManager& history_manager
    );

    friend class JavaLevel;

public:
    AMULET_CORE_EXPORT ~JavaDimension();

    DimensionID dimension_id() override;
    const BlockStack& default_block() override;
    const Biome& default_biome() override;
    std::shared_ptr<ChunkHandle> get_chunk_handle(std::int64_t, std::int64_t) override;
};

} // namespace Amulet
