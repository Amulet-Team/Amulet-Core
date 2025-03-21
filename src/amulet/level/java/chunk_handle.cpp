#include <stdexcept>

#include "chunk_handle.hpp"

namespace Amulet {

bool JavaChunkHandle::exists()
{
    throw std::runtime_error("NotImplementedError");
}
std::shared_ptr<Chunk> JavaChunkHandle::get_chunk()
{
    throw std::runtime_error("NotImplementedError");
}
void JavaChunkHandle::set_chunk(std::shared_ptr<Chunk>)
{
    throw std::runtime_error("NotImplementedError");
}
void JavaChunkHandle::delete_chunk()
{
    throw std::runtime_error("NotImplementedError");
}

} // namespace Amulet
