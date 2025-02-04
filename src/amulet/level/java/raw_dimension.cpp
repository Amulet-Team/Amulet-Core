#include "raw_dimension.hpp"

namespace Amulet {

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
bool JavaRawDimension::has_chunk(std::int64_t cx, std::int64_t cz)
{
    return _anvil_dimension.has_chunk(cx, cz);
}
void JavaRawDimension::delete_chunk(std::int64_t cx, std::int64_t cz)
{
    throw std::runtime_error("NotImplementedError");
}
JavaRawChunk JavaRawDimension::get_raw_chunk(std::int64_t cx, std::int64_t cz)
{
    throw std::runtime_error("NotImplementedError");
}
void JavaRawDimension::set_raw_chunk(std::int64_t cx, std::int64_t cz, const JavaRawChunk& chunk)
{
    throw std::runtime_error("NotImplementedError");
}
void JavaRawDimension::compact()
{
    throw std::runtime_error("NotImplementedError");
}

} // namespace Amulet
