#pragma once
#include <array>
#include <cstdint>

#include <amulet/core/dll.hpp>
#include <amulet/selection/group.hpp>

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
    AMULET_CORE_EXPORT SelectionBox(
        std::int64_t min_x,
        std::int64_t min_y,
        std::int64_t min_z,
        std::uint64_t size_x,
        std::uint64_t size_y,
        std::uint64_t size_z);
    AMULET_CORE_EXPORT SelectionBox(
        std::array<std::int64_t, 3> point_1,
        std::array<std::int64_t, 3> point_2);

    // Accessors
    AMULET_CORE_EXPORT std::int64_t min_x() const;
    AMULET_CORE_EXPORT std::int64_t min_y() const;
    AMULET_CORE_EXPORT std::int64_t min_z() const;
    AMULET_CORE_EXPORT std::int64_t max_x() const;
    AMULET_CORE_EXPORT std::int64_t max_y() const;
    AMULET_CORE_EXPORT std::int64_t max_z() const;
    AMULET_CORE_EXPORT std::array<std::int64_t, 3> min() const;
    AMULET_CORE_EXPORT std::array<std::int64_t, 3> max() const;

    // Shape and volume
    AMULET_CORE_EXPORT std::uint64_t size_x() const;
    AMULET_CORE_EXPORT std::uint64_t size_y() const;
    AMULET_CORE_EXPORT std::uint64_t size_z() const;
    AMULET_CORE_EXPORT std::array<std::uint64_t, 3> shape() const;
    AMULET_CORE_EXPORT size_t volume() const;

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
