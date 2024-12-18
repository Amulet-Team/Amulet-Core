#pragma once
#include <cstdint>
#include <tuple>

#include <amulet/dll.hpp>
#include <amulet/selection/group.hpp>

namespace Amulet {

class SelectionGroup;

// The SelectionBox class represents a single cuboid selection.
class SelectionBox {
private:
    std::tuple<std::int64_t, std::int64_t, std::int64_t> _point_1;
    std::tuple<std::int64_t, std::int64_t, std::int64_t> _point_2;
    std::int64_t _min_x;
    std::int64_t _min_y;
    std::int64_t _min_z;
    std::int64_t _max_x;
    std::int64_t _max_y;
    std::int64_t _max_z;

public:
    AMULET_CORE_DLLX SelectionBox(
        std::tuple<std::int64_t, std::int64_t, std::int64_t> point_1,
        std::tuple<std::int64_t, std::int64_t, std::int64_t> point_2);

    // Accessors
    AMULET_CORE_DLLX std::tuple<std::int64_t, std::int64_t, std::int64_t> point_1() const;
    AMULET_CORE_DLLX std::tuple<std::int64_t, std::int64_t, std::int64_t> point_2() const;
    AMULET_CORE_DLLX std::int64_t min_x() const;
    AMULET_CORE_DLLX std::int64_t min_y() const;
    AMULET_CORE_DLLX std::int64_t min_z() const;
    AMULET_CORE_DLLX std::int64_t max_x() const;
    AMULET_CORE_DLLX std::int64_t max_y() const;
    AMULET_CORE_DLLX std::int64_t max_z() const;
    AMULET_CORE_DLLX std::tuple<std::int64_t, std::int64_t, std::int64_t> min() const;
    AMULET_CORE_DLLX std::tuple<std::int64_t, std::int64_t, std::int64_t> max() const;

    // Shape and volume
    AMULET_CORE_DLLX std::int64_t size_x() const;
    AMULET_CORE_DLLX std::int64_t size_y() const;
    AMULET_CORE_DLLX std::int64_t size_z() const;
    AMULET_CORE_DLLX std::tuple<std::int64_t, std::int64_t, std::int64_t> shape() const;
    AMULET_CORE_DLLX size_t volume() const;

    // Contains and intersects
    AMULET_CORE_DLLX bool contains_block(std::int64_t x, std::int64_t y, std::int64_t z) const;
    AMULET_CORE_DLLX bool contains_point(double x, double y, double z) const;
    AMULET_CORE_DLLX bool contains_box(const SelectionBox& other) const;
    AMULET_CORE_DLLX bool intersects(const SelectionBox& other) const;
    AMULET_CORE_DLLX bool intersects(const SelectionGroup& other) const;
    AMULET_CORE_DLLX bool touches_or_intersects(const SelectionBox& other) const;
    AMULET_CORE_DLLX bool touches(const SelectionBox& other) const;

    // Transform
    AMULET_CORE_DLLX SelectionBox translate(std::int64_t dx, std::int64_t dy, std::int64_t dz) const;
    // AMULET_CORE_DLLX SelectionGroup transform() const;

    // Operators
    auto operator<=>(const SelectionBox&) const = default;
};

} // namespace Amulet
