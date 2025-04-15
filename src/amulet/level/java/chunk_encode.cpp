#include <cstdint>
#include <map>
#include <memory>
#include <stdexcept>

#include <amulet_nbt/tag/named_tag.hpp>

#include <amulet/chunk/chunk.hpp>

#include "chunk.hpp"
#include "raw_dimension.hpp"

namespace Amulet {

JavaRawChunk JavaRawDimension::encode_chunk(
    JavaChunk& chunk, 
    std::int64_t cx, 
    std::int64_t cz)
{
    throw std::runtime_error("");
}

} // namespace Amulet
