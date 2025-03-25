#include <stdexcept>

#include "chunk_handle.hpp"

namespace Amulet {

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
