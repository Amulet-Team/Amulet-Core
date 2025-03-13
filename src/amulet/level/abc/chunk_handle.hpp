#pragma once

#include <cstdint>
#include <memory>
#include <string>

#include <amulet/chunk.hpp>
#include <amulet/utils/mutex.hpp>

namespace Amulet {

using DimensionID = std::string;

class ChunkHandle {
private:
    OrderedMutex _public_mutex;
    std::string _dimension_id;
    std::int64_t _cx;
    std::int64_t _cz;

protected:
    ChunkHandle(
        const DimensionID& dimension_id,
        std::int64_t cx,
        std::int64_t cz)
        : _dimension_id(dimension_id)
        , _cx(cx)
        , _cz(cz)
    {
    }

public:
    virtual ~ChunkHandle() = default;

    AMULET_CORE_EXPORT OrderedMutex& get_mutex() { return _public_mutex; };
    AMULET_CORE_EXPORT const std::string& dimension_id() const { return _dimension_id; }
    AMULET_CORE_EXPORT ::int64_t cx() const { return _cx; }
    AMULET_CORE_EXPORT std::int64_t cz() const { return _cz; }

    virtual bool exists() = 0;
    virtual std::shared_ptr<Chunk> get_chunk() = 0;
    virtual void set_chunk(std::shared_ptr<Chunk>) = 0;
    virtual void delete_chunk() = 0;
};

} // namespace Amulet
