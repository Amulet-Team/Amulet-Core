#include <algorithm>

#include <amulet/selection/box.hpp>
#include <amulet/selection/group.hpp>

namespace Amulet {

AMULET_CORE_DLLX SelectionBox::SelectionBox(
    std::tuple<std::int64_t, std::int64_t, std::int64_t> point_1,
    std::tuple<std::int64_t, std::int64_t, std::int64_t> point_2)
    : _min_x(std::min(std::get<0>(point_1), std::get<0>(point_2)))
    , _min_y(std::min(std::get<1>(point_1), std::get<1>(point_2)))
    , _min_z(std::min(std::get<2>(point_1), std::get<2>(point_2)))
    , _max_x(std::max(std::get<0>(point_1), std::get<0>(point_2)))
    , _max_y(std::max(std::get<1>(point_1), std::get<1>(point_2)))
    , _max_z(std::max(std::get<2>(point_1), std::get<2>(point_2)))
    , _point_1(point_1)
    , _point_2(point_2)
{
}

// Accessors
AMULET_CORE_DLLX std::tuple<std::int64_t, std::int64_t, std::int64_t> SelectionBox::point_1() const
{
    return _point_1;
}
AMULET_CORE_DLLX std::tuple<std::int64_t, std::int64_t, std::int64_t> SelectionBox::point_2() const
{
    return _point_2;
}
AMULET_CORE_DLLX std::int64_t SelectionBox::min_x() const { return _min_x; }
AMULET_CORE_DLLX std::int64_t SelectionBox::min_y() const { return _min_y; }
AMULET_CORE_DLLX std::int64_t SelectionBox::min_z() const { return _min_z; }
AMULET_CORE_DLLX std::int64_t SelectionBox::max_x() const { return _max_x; }
AMULET_CORE_DLLX std::int64_t SelectionBox::max_y() const { return _max_y; }
AMULET_CORE_DLLX std::int64_t SelectionBox::max_z() const { return _max_z; }
AMULET_CORE_DLLX std::tuple<std::int64_t, std::int64_t, std::int64_t> SelectionBox::min() const
{
    return std::make_tuple(_min_x, _min_y, _min_z);
}
AMULET_CORE_DLLX std::tuple<std::int64_t, std::int64_t, std::int64_t> SelectionBox::max() const
{
    return std::make_tuple(_max_x, _max_y, _max_z);
}

// Shape and volume
AMULET_CORE_DLLX std::int64_t SelectionBox::size_x() const
{
    return _max_x - _min_x;
}
AMULET_CORE_DLLX std::int64_t SelectionBox::size_y() const
{
    return _max_y - _min_y;
}
AMULET_CORE_DLLX std::int64_t SelectionBox::size_z() const
{
    return _max_z - _min_z;
}
AMULET_CORE_DLLX std::tuple<std::int64_t, std::int64_t, std::int64_t> SelectionBox::shape() const
{
    return std::make_tuple(_max_x - _min_x, _max_y - _min_y, _max_z - _min_z);
}
AMULET_CORE_DLLX size_t SelectionBox::volume() const
{
    return (_max_x - _min_x) * (_max_y - _min_y) * (_max_z - _min_z);
}

// Contains and intersects
AMULET_CORE_DLLX bool SelectionBox::contains_block(std::int64_t x, std::int64_t y, std::int64_t z) const
{
    return _min_x <= x && x < _max_x
        && _min_y <= y && y < _max_y
        && _min_z <= z && z < _max_z;
}
AMULET_CORE_DLLX bool SelectionBox::contains_point(double x, double y, double z) const
{
    return _min_x <= x && x <= _max_x
        && _min_y <= y && y <= _max_y
        && _min_z <= z && z <= _max_z;
}
AMULET_CORE_DLLX bool SelectionBox::contains_box(const SelectionBox& other) const
{
    return _min_x <= other._min_x
        && _min_y <= other._min_y
        && _min_z <= other._min_z
        && other._max_x <= _max_x
        && other._max_y <= _max_y
        && other._max_z <= _max_z;
}
AMULET_CORE_DLLX bool SelectionBox::intersects(const SelectionBox& other) const
{
    return _min_x < other._max_x && other._min_x < _max_x
        && _min_y < other._max_y && other._min_y < _max_y
        && _min_z < other._max_z && other._min_z < _max_z;
}
AMULET_CORE_DLLX bool SelectionBox::intersects(const SelectionGroup& other) const
{
    return other.intersects(*this);
}
AMULET_CORE_DLLX bool SelectionBox::touches_or_intersects(const SelectionBox& other) const
{
    return _min_x <= other._max_x && other._min_x <= _max_x
        && _min_y <= other._max_y && other._min_y <= _max_y
        && _min_z <= other._max_z && other._min_z <= _max_z;
};
AMULET_CORE_DLLX bool SelectionBox::touches(const SelectionBox& other) const
{
    return touches_or_intersects(other) && !intersects(other);
}

// Transform
AMULET_CORE_DLLX SelectionBox SelectionBox::translate(std::int64_t dx, std::int64_t dy, std::int64_t dz) const
{
    return SelectionBox(
        std::make_tuple(_min_x + dx, _min_y + dy, _min_z + dz),
        std::make_tuple(_max_x + dx, _max_y + dy, _max_z + dz));
}
// AMULET_CORE_DLLX SelectionGroup SelectionBox::transform() const;

} // namespace Amulet
