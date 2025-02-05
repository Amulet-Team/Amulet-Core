#include <mutex>
#include <shared_mutex>

#include "raw_dimension.hpp"

namespace Amulet {

AnvilChunkCoordIterator JavaRawDimension::all_chunk_coords()
{
    return _anvil_dimension.all_chunk_coords();
}

bool JavaRawDimension::has_chunk(std::int64_t cx, std::int64_t cz)
{
    auto& mutex = _anvil_dimension.mutex();
    mutex.lock_shared_read();
    std::unique_lock lock(mutex, std::adopt_lock);
    return _anvil_dimension.has_chunk(cx, cz);
}
void JavaRawDimension::delete_chunk(std::int64_t cx, std::int64_t cz)
{
    auto& mutex = _anvil_dimension.mutex();
    mutex.lock_shared_read_write();
    std::unique_lock lock(mutex, std::adopt_lock);
    _anvil_dimension.delete_chunk(cx, cz);
}
JavaRawChunk JavaRawDimension::get_raw_chunk(std::int64_t cx, std::int64_t cz)
{
    auto& mutex = _anvil_dimension.mutex();
    mutex.lock_shared_read();
    std::unique_lock lock(mutex, std::adopt_lock);
    return _anvil_dimension.get_chunk_data(cx, cz);
}
void JavaRawDimension::set_raw_chunk(std::int64_t cx, std::int64_t cz, const JavaRawChunk& chunk)
{
    auto& mutex = _anvil_dimension.mutex();
    mutex.lock_shared_read_write();
    std::unique_lock lock(mutex, std::adopt_lock);
    _anvil_dimension.set_chunk_data(cx, cz, chunk);
}
void JavaRawDimension::compact()
{
    std::unique_lock lock(_anvil_dimension.mutex());
    _anvil_dimension.compact();
}

} // namespace Amulet
