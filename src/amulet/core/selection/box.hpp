#pragma once
#include <array>
#include <cstdint>

#include <amulet/core/dll.hpp>

namespace Amulet {

class Matrix4x4;
class SelectionBoxGroup;

// An axis aligned cuboid selection box.
class AMULET_CORE_EXPORT SelectionBox {
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

    SelectionBox(const SelectionBox& other)
        : SelectionBox(
              other.min_x(),
              other.min_y(),
              other.min_z(),
              other.size_x(),
              other.size_y(),
              other.size_z())
    {
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
    std::uint64_t volume() const { return _size_x * _size_y * _size_z; }

    // Contains and intersects
    bool contains_block(std::int64_t x, std::int64_t y, std::int64_t z) const;
    bool contains_point(double x, double y, double z) const;
    bool contains_box(const SelectionBox& other) const;
    bool intersects(const SelectionBox& other) const;
    bool intersects(const SelectionBoxGroup& other) const;
    bool touches_or_intersects(const SelectionBox& other) const;
    bool touches(const SelectionBox& other) const;

    // Transform
    SelectionBox translate(std::int64_t dx, std::int64_t dy, std::int64_t dz) const;
    SelectionBoxGroup transform(const Matrix4x4&) const;

    // Operators
    std::strong_ordering operator<=>(const SelectionBox&) const;
    bool operator==(const SelectionBox&) const;
};

} // namespace Amulet
