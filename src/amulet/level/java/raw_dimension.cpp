#include <mutex>
#include <shared_mutex>

#include "raw_dimension.hpp"

namespace Amulet {

JavaRawDimension::~JavaRawDimension()
{
    destroy();
}

OrderedMutex& JavaRawDimension::get_mutex()
{
    return _public_mutex;
}

const DimensionID& JavaRawDimension::get_dimension_id() const
{
    return _dimension_id;
}

const JavaInternalDimensionID& JavaRawDimension::get_relative_path() const
{
    return _relative_path;
}

const SelectionBox& JavaRawDimension::get_bounds() const
{
    return _bounds;
}

const BlockStack& JavaRawDimension::get_default_block() const
{
    return _default_block;
}

const Biome& JavaRawDimension::get_default_biome() const
{
    return _default_biome;
}

AnvilChunkCoordIterator JavaRawDimension::all_chunk_coords() const
{
    return _anvil_dimension.all_chunk_coords();
}

bool JavaRawDimension::has_chunk(std::int64_t cx, std::int64_t cz)
{
    auto& mutex = _anvil_dimension.get_mutex();
    mutex.lock<ThreadAccessMode::Read, ThreadShareMode::SharedReadWrite>();
    std::lock_guard lock(mutex, std::adopt_lock);
    return _anvil_dimension.has_chunk(cx, cz);
}
void JavaRawDimension::delete_chunk(std::int64_t cx, std::int64_t cz)
{
    auto& mutex = _anvil_dimension.get_mutex();
    mutex.lock<ThreadAccessMode::ReadWrite, ThreadShareMode::SharedReadWrite>();
    std::lock_guard lock(mutex, std::adopt_lock);
    _anvil_dimension.delete_chunk(cx, cz);
}
JavaRawChunk JavaRawDimension::get_raw_chunk(std::int64_t cx, std::int64_t cz)
{
    auto& mutex = _anvil_dimension.get_mutex();
    mutex.lock<ThreadAccessMode::Read, ThreadShareMode::SharedReadWrite>();
    std::lock_guard lock(mutex, std::adopt_lock);
    return _anvil_dimension.get_chunk_data(cx, cz);
}
void JavaRawDimension::set_raw_chunk(std::int64_t cx, std::int64_t cz, const JavaRawChunk& chunk)
{
    auto& mutex = _anvil_dimension.get_mutex();
    mutex.lock<ThreadAccessMode::ReadWrite, ThreadShareMode::SharedReadWrite>();
    std::lock_guard lock(mutex, std::adopt_lock);
    _anvil_dimension.set_chunk_data(cx, cz, chunk);
}
void JavaRawDimension::compact()
{
    auto& mutex = _anvil_dimension.get_mutex();
    mutex.lock<ThreadAccessMode::ReadWrite, ThreadShareMode::SharedReadOnly>();
    std::lock_guard lock(mutex, std::adopt_lock);
    _anvil_dimension.compact();
}

void JavaRawDimension::destroy()
{
    _destroyed = true;
    std::lock_guard lock(_anvil_dimension.get_mutex());
    _anvil_dimension.destroy();
}

bool JavaRawDimension::is_destroyed()
{
    return _destroyed;
}

} // namespace Amulet
