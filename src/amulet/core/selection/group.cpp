#include <limits>
#include <stdexcept>

#include "box.hpp"
#include "group.hpp"

namespace Amulet {

// Bounds
std::int64_t SelectionGroup::min_x() const
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
std::int64_t SelectionGroup::min_y() const
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
std::int64_t SelectionGroup::min_z() const
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
std::int64_t SelectionGroup::max_x() const
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
std::int64_t SelectionGroup::max_y() const
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
std::int64_t SelectionGroup::max_z() const
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
std::array<std::int64_t, 3> SelectionGroup::min() const
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
    return { x, y, z };
}
std::array<std::int64_t, 3> SelectionGroup::max() const
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
    return { x, y, z };
}
std::pair<
    std::array<std::int64_t, 3>,
    std::array<std::int64_t, 3>>
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
        std::array<std::int64_t, 3>({ x_min, y_min, z_min }),
        std::array<std::int64_t, 3>({ x_max, y_max, z_max }));
}
SelectionBox SelectionGroup::bounding_box() const
{
    auto [min_point, max_point] = bounds();
    return SelectionBox(
        min_point[0],
        min_point[1],
        min_point[2],
        max_point[0] - min_point[0],
        max_point[1] - min_point[1],
        max_point[2] - min_point[2]);
}

// Contains and intersects
bool SelectionGroup::contains_block(std::int64_t x, std::int64_t y, std::int64_t z) const
{
    for (const auto& box : _boxes) {
        if (box.contains_block(x, y, z)) {
            return true;
        }
    }
    return false;
}
bool SelectionGroup::contains_point(double x, double y, double z) const
{
    for (const auto& box : _boxes) {
        if (box.contains_point(x, y, z)) {
            return true;
        }
    }
    return false;
}
bool SelectionGroup::intersects(const SelectionBox& other) const
{
    for (const auto& box : _boxes) {
        if (box.intersects(other)) {
            return true;
        }
    }
    return false;
}
bool SelectionGroup::intersects(const SelectionGroup& other) const
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
SelectionGroup SelectionGroup::translate(std::int64_t dx, std::int64_t dy, std::int64_t dz) const
{
    SelectionGroup group;
    for (const auto& box : _boxes) {
        group._boxes.emplace(
            box.min_x() + dx,
            box.min_y() + dy,
            box.min_z() + dz,
            box.size_x(),
            box.size_y(),
            box.size_z());
    }
    return group;
}

} // namespace Amulet
