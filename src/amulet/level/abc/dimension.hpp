#pragma once

#include <memory>
#include <string>
#include <variant>

#include <amulet/biome/biome.hpp>
#include <amulet/block/block.hpp>
#include <amulet/selection/box.hpp>
#include <amulet/selection/group.hpp>

#include "chunk_handle.hpp"

namespace Amulet {

using DimensionID = std::string;

class Dimension {
public:
    // Destructor
    virtual ~Dimension() = default;

    // Get the dimension id for this dimension.
    // Thread safe.
    virtual const DimensionID& get_dimension_id() const = 0;

    // The editable region of the dimension.
    // Thread safe.
    virtual std::variant<SelectionBox, SelectionGroup> get_bounds() const = 0;

    // Get the default block for this dimension.
    // Thread safe.
    virtual const BlockStack& get_default_block() const = 0;

    // Get the default biome for this dimension.
    // Thread safe.
    virtual const Biome& get_default_biome() const = 0;

    // TODO
    // chunk_coords
    // changed_chunk_coords

    // Get a chunk handle for a specific chunk.
    // Thread safe.
    virtual std::shared_ptr<ChunkHandle> get_chunk_handle(std::int64_t cx, std::int64_t cz) = 0;
};

} // namespace Amulet
