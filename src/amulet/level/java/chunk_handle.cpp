#include <stdexcept>

#include "chunk_handle.hpp"

namespace Amulet {

JavaChunkHandle::JavaChunkHandle(
    const DimensionID& dimension_id,
    std::int64_t cx,
    std::int64_t cz,
    std::shared_ptr<JavaRawDimension> raw_dimension,
    std::shared_ptr<HistoryManagerLayer<detail::ChunkKey>> chunk_history,
    std::shared_ptr<HistoryManagerLayer<std::string>> chunk_data_history)
    : ChunkHandle(dimension_id, cx, cz)
    , _raw_dimension(std::move(raw_dimension))
    , _chunk_history(std::move(chunk_history))
    , _chunk_data_history(std::move(chunk_data_history))
{
}

bool JavaChunkHandle::exists()
{
    throw std::runtime_error("NotImplementedError");
}

std::unique_ptr<JavaChunk> JavaChunkHandle::get_java_chunk()
{
    throw std::runtime_error("NotImplementedError");
}

std::unique_ptr<Chunk> JavaChunkHandle::get_chunk()
{
    return get_java_chunk();
}

void JavaChunkHandle::set_java_chunk(const JavaChunk& chunk)
{
    throw std::runtime_error("NotImplementedError");
}

void JavaChunkHandle::set_chunk(const Chunk& chunk)
{
    auto* java_chunk = dynamic_cast<const JavaChunk*>(&chunk);
    if (!java_chunk) {
        throw std::invalid_argument("chunk is not an instance of JavaChunk");
    }
    set_java_chunk(*java_chunk);
}

void JavaChunkHandle::delete_chunk()
{
    throw std::runtime_error("NotImplementedError");
}

} // namespace Amulet
