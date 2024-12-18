#include <limits>
#include <stdexcept>

#include <amulet/selection/box.hpp>
#include <amulet/selection/group.hpp>

namespace Amulet {

// Constructors
AMULET_CORE_DLLX SelectionGroup::SelectionGroup(const SelectionBox& box)
{
    _boxes.insert(box);
}

// Accessors
AMULET_CORE_DLLX const std::set<SelectionBox>& SelectionGroup::selection_boxes()
{
    return _boxes;
}
AMULET_CORE_DLLX std::int64_t SelectionGroup::min_x() const
{
    if (_boxes.empty()) {
        throw std::runtime_error("Empty SelectionGroup has no minimum");
    }
    std::int64_t value = std::numeric_limits<std::int64_t>::max();
    for (const auto& box : _boxes) {
        if (box.min_x() < value) {
            value = box.min_x();
        }
    }
    return value;
}
AMULET_CORE_DLLX std::int64_t SelectionGroup::min_y() const
{
    if (_boxes.empty()) {
        throw std::runtime_error("Empty SelectionGroup has no minimum");
    }
    std::int64_t value = std::numeric_limits<std::int64_t>::max();
    for (const auto& box : _boxes) {
        if (box.min_y() < value) {
            value = box.min_y();
        }
    }
    return value;
}
AMULET_CORE_DLLX std::int64_t SelectionGroup::min_z() const
{
    if (_boxes.empty()) {
        throw std::runtime_error("Empty SelectionGroup has no minimum");
    }
    std::int64_t value = std::numeric_limits<std::int64_t>::max();
    for (const auto& box : _boxes) {
        if (box.min_z() < value) {
            value = box.min_z();
        }
    }
    return value;
}
AMULET_CORE_DLLX std::int64_t SelectionGroup::max_x() const
{
    if (_boxes.empty()) {
        throw std::runtime_error("Empty SelectionGroup has no maximum");
    }
    std::int64_t value = std::numeric_limits<std::int64_t>::min();
    for (const auto& box : _boxes) {
        if (value < box.max_x()) {
            value = box.max_x();
        }
    }
    return value;
}
AMULET_CORE_DLLX std::int64_t SelectionGroup::max_y() const
{
    if (_boxes.empty()) {
        throw std::runtime_error("Empty SelectionGroup has no maximum");
    }
    std::int64_t value = std::numeric_limits<std::int64_t>::min();
    for (const auto& box : _boxes) {
        if (value < box.max_y()) {
            value = box.max_y();
        }
    }
    return value;
}
AMULET_CORE_DLLX std::int64_t SelectionGroup::max_z() const
{
    if (_boxes.empty()) {
        throw std::runtime_error("Empty SelectionGroup has no maximum");
    }
    std::int64_t value = std::numeric_limits<std::int64_t>::min();
    for (const auto& box : _boxes) {
        if (value < box.max_z()) {
            value = box.max_z();
        }
    }
    return value;
}
AMULET_CORE_DLLX std::tuple<std::int64_t, std::int64_t, std::int64_t> SelectionGroup::min() const
{
    if (_boxes.empty()) {
        throw std::runtime_error("Empty SelectionGroup has no minimum");
    }
    std::int64_t x = std::numeric_limits<std::int64_t>::max();
    std::int64_t y = std::numeric_limits<std::int64_t>::max();
    std::int64_t z = std::numeric_limits<std::int64_t>::max();
    for (const auto& box : _boxes) {
        if (box.min_x() < x) {
            x = box.min_x();
        }
        if (box.min_y() < y) {
            y = box.min_y();
        }
        if (box.min_z() < z) {
            z = box.min_z();
        }
    }
    return std::make_tuple(x, y, z);
}
AMULET_CORE_DLLX std::tuple<std::int64_t, std::int64_t, std::int64_t> SelectionGroup::max() const
{
    if (_boxes.empty()) {
        throw std::runtime_error("Empty SelectionGroup has no maximum");
    }
    std::int64_t x = std::numeric_limits<std::int64_t>::min();
    std::int64_t y = std::numeric_limits<std::int64_t>::min();
    std::int64_t z = std::numeric_limits<std::int64_t>::min();
    for (const auto& box : _boxes) {
        if (x < box.max_x()) {
            x = box.max_x();
        }
        if (y < box.max_y()) {
            y = box.max_y();
        }
        if (z < box.max_z()) {
            z = box.max_z();
        }
    }
    return std::make_tuple(x, y, z);
}
AMULET_CORE_DLLX std::pair<
    std::tuple<std::int64_t, std::int64_t, std::int64_t>,
    std::tuple<std::int64_t, std::int64_t, std::int64_t>>
SelectionGroup::bounds() const
{
    if (_boxes.empty()) {
        throw std::runtime_error("Empty SelectionGroup has no minimum or maximum");
    }
    std::int64_t x_min = std::numeric_limits<std::int64_t>::max();
    std::int64_t y_min = std::numeric_limits<std::int64_t>::max();
    std::int64_t z_min = std::numeric_limits<std::int64_t>::max();
    std::int64_t x_max = std::numeric_limits<std::int64_t>::min();
    std::int64_t y_max = std::numeric_limits<std::int64_t>::min();
    std::int64_t z_max = std::numeric_limits<std::int64_t>::min();
    for (const auto& box : _boxes) {
        if (box.min_x() < x_min) {
            x_min = box.min_x();
        }
        if (box.min_y() < y_min) {
            y_min = box.min_y();
        }
        if (box.min_z() < z_min) {
            z_min = box.min_z();
        }
        if (x_max < box.max_x()) {
            x_max = box.max_x();
        }
        if (y_max < box.max_y()) {
            y_max = box.max_y();
        }
        if (z_max < box.max_z()) {
            z_max = box.max_z();
        }
    }
    return std::make_pair(
        std::make_tuple(x_min, y_min, z_min),
        std::make_tuple(x_max, y_max, z_max));
}
AMULET_CORE_DLLX SelectionBox SelectionGroup::bounding_box() const
{
    auto [point_1, point_2] = bounds();
    return SelectionBox(point_1, point_2);
}

// Contains and intersects
AMULET_CORE_DLLX bool SelectionGroup::contains_block(std::int64_t x, std::int64_t y, std::int64_t z) const
{
    for (const auto& box : _boxes) {
        if (box.contains_block(x, y, z)) {
            return true;
        }
    }
    return false;
}
AMULET_CORE_DLLX bool SelectionGroup::contains_point(double x, double y, double z) const
{
    for (const auto& box : _boxes) {
        if (box.contains_point(x, y, z)) {
            return true;
        }
    }
    return false;
}
AMULET_CORE_DLLX bool SelectionGroup::intersects(const SelectionBox& other) const
{
    for (const auto& box : _boxes) {
        if (box.intersects(other)) {
            return true;
        }
    }
    return false;
}
AMULET_CORE_DLLX bool SelectionGroup::intersects(const SelectionGroup& other) const
{
    for (const auto& box_1 : _boxes) {
        for (const auto& box_2 : other._boxes) {
            if (box_1.intersects(box_2)) {
                return true;
            }
        }
    }
    return false;
}

// Transform
AMULET_CORE_DLLX SelectionGroup SelectionGroup::translate(std::int64_t dx, std::int64_t dy, std::int64_t dz) const
{
    SelectionGroup group;
    for (const auto& box : _boxes) {
        const auto& point_1 = box.point_1();
        const auto& point_2 = box.point_2();
        group._boxes.emplace(
            std::make_tuple(
                std::get<0>(point_1),
                std::get<1>(point_1),
                std::get<2>(point_1)),
            std::make_tuple(
                std::get<0>(point_2),
                std::get<1>(point_2),
                std::get<2>(point_2)));
    }
    return group;
}

// Operators
AMULET_CORE_DLLX SelectionGroup::operator bool() const
{
    return !_boxes.empty();
}

} // namespace Amulet
