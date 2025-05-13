#pragma once
#include <array>
#include <cstdint>

#include <amulet/core/dll.hpp>

namespace Amulet {

class SelectionGroup;

// The SelectionBox class represents a single cuboid selection.
class SelectionBox {
private:
    std::int64_t _min_x;
    std::int64_t _min_y;
    std::int64_t _min_z;
    std::uint64_t _size_x;
    std::uint64_t _size_y;
    std::uint64_t _size_z;

public:
    SelectionBox(
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

    SelectionBox(
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
    std::int64_t min_x() const { return _min_x; }
    std::int64_t min_y() const { return _min_y; }
    std::int64_t min_z() const { return _min_z; }
    std::int64_t max_x() const { return _min_x + _size_x; }
    std::int64_t max_y() const { return _min_y + _size_y; }
    std::int64_t max_z() const { return _min_z + _size_z; }
    std::array<std::int64_t, 3> min() const { return { _min_x, _min_y, _min_z }; }
    std::array<std::int64_t, 3> max() const { return { max_x(), max_y(), max_z() }; }

    // Shape and volume
    std::uint64_t size_x() const { return _size_x; }
    std::uint64_t size_y() const { return _size_y; }
    std::uint64_t size_z() const { return _size_z; }
    std::array<std::uint64_t, 3> shape() const { return { _size_x, _size_y, _size_z }; }
    size_t volume() const { return _size_x * _size_y * _size_z; }

    // Contains and intersects
    AMULET_CORE_EXPORT bool contains_block(std::int64_t x, std::int64_t y, std::int64_t z) const;
    AMULET_CORE_EXPORT bool contains_point(double x, double y, double z) const;
    AMULET_CORE_EXPORT bool contains_box(const SelectionBox& other) const;
    AMULET_CORE_EXPORT bool intersects(const SelectionBox& other) const;
    AMULET_CORE_EXPORT bool intersects(const SelectionGroup& other) const;
    AMULET_CORE_EXPORT bool touches_or_intersects(const SelectionBox& other) const;
    AMULET_CORE_EXPORT bool touches(const SelectionBox& other) const;

    // Transform
    AMULET_CORE_EXPORT SelectionBox translate(std::int64_t dx, std::int64_t dy, std::int64_t dz) const;
    // AMULET_CORE_EXPORT SelectionGroup transform() const;

    // Operators
    auto operator<=>(const SelectionBox&) const = default;
};

} // namespace Amulet

#include "group.hpp"
