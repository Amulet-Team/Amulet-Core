#pragma once

#include <cstdint>
#include <memory>
#include <string>

#include <amulet/chunk.hpp>

namespace Amulet {

class ChunkHandle {
public:
    virtual ~ChunkHandle() { }
    virtual std::string dimension_id() = 0;
    virtual std::int64_t cx() = 0;
    virtual std::int64_t cz() = 0;
    virtual bool exists() = 0;
    virtual std::shared_ptr<Chunk> get_chunk() = 0;
    virtual void set_chunk(std::shared_ptr<Chunk>) = 0;
    virtual void delete_chunk() = 0;
};

} // namespace Amulet
