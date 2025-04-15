#include "chunk_handle.hpp"

namespace Amulet {

namespace detail {
    ChunkKey::ChunkKey(std::int64_t cx, std::int64_t cz)
        : cx(cx)
        , cz(cz)
    {
    }

    ChunkKey::~ChunkKey() { }

    std::int64_t ChunkKey::get_cx() const
    {
        return cx;
    }

    std::int64_t ChunkKey::get_cz() const
    {
        return cz;
    }

    ChunkKey::operator std::string() const
    {
        std::string str(2 * sizeof(std::int64_t) + 1, '/');
        *reinterpret_cast<std::int64_t*>(str.data()) = cx;
        *reinterpret_cast<std::int64_t*>(str.data() + sizeof(std::int64_t) + 1) = cz;
        return str;
    }
} // namespace detail

ChunkHandle::ChunkHandle(
    const DimensionID& dimension_id,
    std::int64_t cx,
    std::int64_t cz)
    : _dimension_id(dimension_id)
    , _cx(cx)
    , _cz(cz)
    , _key(cx, cz)
{
}

OrderedMutex& ChunkHandle::get_mutex() { return _public_mutex; }

const std::string& ChunkHandle::get_dimension_id() const { return _dimension_id; }

std::int64_t ChunkHandle::get_cx() const { return _cx; }

std::int64_t ChunkHandle::get_cz() const { return _cz; }

} // namespace Amulet
