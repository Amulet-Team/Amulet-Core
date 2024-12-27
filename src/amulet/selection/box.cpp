#include <algorithm>
#include <array>

#include <amulet/selection/box.hpp>
#include <amulet/selection/group.hpp>

namespace Amulet {

AMULET_CORE_DLLX SelectionBox::SelectionBox(
    std::int64_t min_x,
    std::int64_t min_y,
    std::int64_t min_z,
    std::uint64_t size_x,
    std::uint64_t size_y,
    std::uint64_t size_z)
    : _min_x(min_x)
    , _min_y(min_y)
    , _min_z(min_z)
    , _size_x(size_x)
    , _size_y(size_y)
    , _size_z(size_z)
{
}

AMULET_CORE_DLLX SelectionBox::SelectionBox(
    std::array<std::int64_t, 3> point_1,
    std::array<std::int64_t, 3> point_2)
{
    _min_x = std::min(point_1[0], point_2[0]);
    _min_y = std::min(point_1[1], point_2[1]);
    _min_z = std::min(point_1[2], point_2[2]);
    _size_x = std::max(point_1[0], point_2[0]) - _min_x;
    _size_y = std::max(point_1[1], point_2[1]) - _min_y;
    _size_z = std::max(point_1[2], point_2[2]) - _min_z;
}

// Accessors
AMULET_CORE_DLLX std::int64_t SelectionBox::min_x() const { return _min_x; }
AMULET_CORE_DLLX std::int64_t SelectionBox::min_y() const { return _min_y; }
AMULET_CORE_DLLX std::int64_t SelectionBox::min_z() const { return _min_z; }
AMULET_CORE_DLLX std::int64_t SelectionBox::max_x() const { return _min_x + _size_x; }
AMULET_CORE_DLLX std::int64_t SelectionBox::max_y() const { return _min_y + _size_y; }
AMULET_CORE_DLLX std::int64_t SelectionBox::max_z() const { return _min_z + _size_z; }
AMULET_CORE_DLLX std::array<std::int64_t, 3> SelectionBox::min() const
{
    return { _min_x, _min_y, _min_z };
}
AMULET_CORE_DLLX std::array<std::int64_t, 3> SelectionBox::max() const
{
    return { max_x(), max_y(), max_z() };
}

// Shape and volume
AMULET_CORE_DLLX std::uint64_t SelectionBox::size_x() const
{
    return _size_x;
}
AMULET_CORE_DLLX std::uint64_t SelectionBox::size_y() const
{
    return _size_y;
}
AMULET_CORE_DLLX std::uint64_t SelectionBox::size_z() const
{
    return _size_z;
}
AMULET_CORE_DLLX std::array<std::uint64_t, 3> SelectionBox::shape() const
{
    return { _size_x, _size_y, _size_z };
}
AMULET_CORE_DLLX size_t SelectionBox::volume() const
{
    return _size_x * _size_y * _size_z;
}

// Contains and intersects
AMULET_CORE_DLLX bool SelectionBox::contains_block(std::int64_t x, std::int64_t y, std::int64_t z) const
{
    return _min_x <= x && x < max_x()
        && _min_y <= y && y < max_y()
        && _min_z <= z && z < max_z();
}
AMULET_CORE_DLLX bool SelectionBox::contains_point(double x, double y, double z) const
{
    return _min_x <= x && x <= max_x()
        && _min_y <= y && y <= max_y()
        && _min_z <= z && z <= max_z();
}
AMULET_CORE_DLLX bool SelectionBox::contains_box(const SelectionBox& other) const
{
    return _min_x <= other._min_x
        && _min_y <= other._min_y
        && _min_z <= other._min_z
        && other.max_x() <= max_x()
        && other.max_y() <= max_y()
        && other.max_z() <= max_z();
}
AMULET_CORE_DLLX bool SelectionBox::intersects(const SelectionBox& other) const
{
    return _min_x < other.max_x() && other._min_x < max_x()
        && _min_y < other.max_y() && other._min_y < max_y()
        && _min_z < other.max_z() && other._min_z < max_z();
}
AMULET_CORE_DLLX bool SelectionBox::intersects(const SelectionGroup& other) const
{
    return other.intersects(*this);
}
AMULET_CORE_DLLX bool SelectionBox::touches_or_intersects(const SelectionBox& other) const
{
    return _min_x <= other.max_x() && other._min_x <= max_x()
        && _min_y <= other.max_y() && other._min_y <= max_y()
        && _min_z <= other.max_z() && other._min_z <= max_z();
};
AMULET_CORE_DLLX bool SelectionBox::touches(const SelectionBox& other) const
{
    return touches_or_intersects(other) && !intersects(other);
}

// Transform
AMULET_CORE_DLLX SelectionBox SelectionBox::translate(std::int64_t dx, std::int64_t dy, std::int64_t dz) const
{
    return SelectionBox(
        _min_x + dx,
        _min_y + dy,
        _min_z + dz,
        _size_x,
        _size_y,
        _size_z);
}
// AMULET_CORE_DLLX SelectionGroup SelectionBox::transform() const;

} // namespace Amulet
