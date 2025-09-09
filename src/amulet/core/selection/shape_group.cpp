#include "shape_group.hpp"
#include "box.hpp"
#include "box_group.hpp"

namespace Amulet {

SelectionShapeGroup::operator std::set<SelectionBox>() const
{
    std::set<SelectionBox> boxes;
    for (const auto& shape : _shapes) {
        auto shape_boxes = static_cast<std::set<SelectionBox>>(*shape);
        boxes.insert(shape_boxes.begin(), shape_boxes.end());
    }
    return boxes;
}

SelectionShapeGroup::operator SelectionBoxGroup() const
{
    return static_cast<std::set<SelectionBox>>(*this);
}

SelectionBoxGroup SelectionShapeGroup::voxelise() const
{
    return static_cast<SelectionBoxGroup>(*this);
}

bool SelectionShapeGroup::almost_equal(const SelectionShapeGroup& other) const
{
    if (count() != other.count()) {
        return false;
    }
    auto& shapes1 = get_shapes();
    auto& shapes2 = other.get_shapes();
    for (size_t i = 0; i < shapes1.size(); i++) {
        if (!shapes1[i]->almost_equal(*shapes2[i])) {
            return false;
        }
    }
    return true;
}

bool SelectionShapeGroup::operator == (const SelectionShapeGroup& other) const
{
    if (count() != other.count()) {
        return false;
    }
    const auto& shapes = get_shapes();
    const auto& other_shapes = other.get_shapes();
    for (size_t i = 0; i < shapes.size(); i++) {
        if (*shapes[i] != *other_shapes[i]) {
            return false;
        }
    }
    return true;
}

} // namespace Amulet
