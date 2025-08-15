#include "shape_group.hpp"
#include "box_group.hpp"

namespace Amulet {

SelectionBoxGroup SelectionShapeGroup::voxelise() const
{
    std::set<SelectionBox> boxes;
    for (const auto& shape : _shapes) {
        auto shape_boxes = shape->voxelise();
        boxes.insert(shape_boxes.begin(), shape_boxes.end());
    }
    return SelectionBoxGroup(std::move(boxes));
}

SelectionShapeGroup::operator SelectionBoxGroup() const
{
    return voxelise();
}
SelectionShapeGroup::operator std::set<SelectionBox>() const
{
    return voxelise().selection_boxes();
}

}
