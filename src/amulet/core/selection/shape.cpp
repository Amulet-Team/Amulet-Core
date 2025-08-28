#include "shape.hpp"
#include "box_group.hpp"

namespace Amulet {

const Matrix4x4& SelectionShape::get_matrix() const
{
    return _matrix;
}

SelectionShape::operator SelectionBoxGroup() const
{
    return static_cast<std::set<SelectionBox>>(*this);
}

SelectionBoxGroup SelectionShape::voxelise() const
{
    return static_cast<SelectionBoxGroup>(*this);
}

} // namespace Amulet
