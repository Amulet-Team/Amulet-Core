#include "dimension.hpp"

namespace Amulet {

JavaDimension::JavaDimension(
    std::shared_ptr<JavaRawDimension> raw_dimension,
    HistoryManager& history_manager)
{
}

JavaDimension::~JavaDimension()
{
}

DimensionID JavaDimension::dimension_id()
{
    throw std::runtime_error("NotImplementedError");
}

const BlockStack& JavaDimension::default_block()
{
    throw std::runtime_error("NotImplementedError");
}

const Biome& JavaDimension::default_biome()
{
    throw std::runtime_error("NotImplementedError");
}

std::shared_ptr<ChunkHandle> JavaDimension::get_chunk_handle(std::int64_t, std::int64_t)
{
    throw std::runtime_error("NotImplementedError");
}

} // namespace Amulet
