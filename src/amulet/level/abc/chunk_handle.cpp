#include "chunk_handle.hpp"

namespace Amulet {

ChunkHandle::ChunkHandle(
    const DimensionID& dimension_id,
    std::int64_t cx,
    std::int64_t cz)
    : _dimension_id(dimension_id)
    , _cx(cx)
    , _cz(cz)
{
}

OrderedMutex& ChunkHandle::get_mutex() { return _public_mutex; }

const std::string& ChunkHandle::get_dimension_id() const { return _dimension_id; }

std::int64_t ChunkHandle::get_cx() const { return _cx; }

std::int64_t ChunkHandle::get_cz() const { return _cz; }

} // namespace Amulet
