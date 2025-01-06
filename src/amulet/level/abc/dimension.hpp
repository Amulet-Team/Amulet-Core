#pragma once

#include <memory>
#include <string>

#include <amulet/biome.hpp>
#include <amulet/block.hpp>

#include "chunk_handle.hpp"

namespace Amulet {

class Dimension {
public:
    virtual ~Dimension() { }
    virtual std::string dimension_id() = 0;
    virtual const BlockStack& default_block() = 0;
    virtual const Biome& default_biome() = 0;
    virtual std::shared_ptr<ChunkHandle> get_chunk_handle(std::int64_t, std::int64_t) = 0;
};

} // namespace Amulet
