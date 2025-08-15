#include <cmath>

#include "sphere.hpp"
#include "box.hpp"

namespace Amulet {

std::set<SelectionBox> SelectionSphere::voxelise() const
{
    std::set<SelectionBox> boxes;
    auto radius = std::abs(_radius);
    auto min_x = std::round(_x - radius) + 0.5;
    auto max_x = std::round(_x + radius) - 0.5;
    for (auto x = min_x; x <= max_x; x++) {
        // Process the sphere in circular slices
        auto slice_radius_square = std::pow(radius, 2) - std::pow(_x - x, 2);
        auto slice_radius = std::pow(slice_radius_square, 0.5);
        auto min_z = std::round(_z - slice_radius) + 0.5;
        auto max_z = std::round(_z + slice_radius) - 0.5;
        for (auto z = min_z; z <= max_z; z++) {
            auto box_radius = std::pow(slice_radius_square - std::pow(_z - z, 2), 0.5);
            auto min_y = std::round(_y - box_radius);
            auto max_y = std::round(_y + box_radius);
            boxes.emplace( 
                static_cast<std::int64_t>(x),
                static_cast<std::int64_t>(min_y),
                static_cast<std::int64_t>(z),
                static_cast<std::int64_t>(1),
                static_cast<std::int64_t>(max_y - min_y),
                static_cast<std::int64_t>(1)
            );
        }
    }
    return boxes;
}

std::unique_ptr<SelectionShape> SelectionSphere::copy() const
{
    return std::make_unique<SelectionSphere>(*this);
}

SelectionSphere SelectionSphere::translate(double dx, double dy, double dz) const
{
    return SelectionSphere(_x + dx, _y + dy, _z + dz, _radius);
}

bool SelectionSphere::operator==(const SelectionSphere& other) const
{
    return _x == other._x && _y == other._y && _z == other._z && _radius == other._radius;
}

} // namespace Amulet
