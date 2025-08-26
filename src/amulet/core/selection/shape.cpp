#include "shape.hpp"
#include "box_group.hpp"

namespace Amulet {

SelectionShape::operator SelectionBoxGroup() const
{
    return static_cast<std::set<SelectionBox>>(*this);
}

SelectionBoxGroup SelectionShape::voxelise() const
{
    return static_cast<SelectionBoxGroup>(*this);
}

} // namespace Amulet
