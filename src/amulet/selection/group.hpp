#pragma once

#include <set>

#include <amulet/dll.hpp>
#include <amulet/selection/box.hpp>

namespace Amulet {

class SelectionBox;

class SelectionGroup {
private:
    std::set<SelectionBox> _boxes;

public:
    // Constructors
    SelectionGroup() {};
    AMULET_CORE_DLLX SelectionGroup(const SelectionBox& box);
    template <typename Iterable>
    SelectionGroup(const Iterable& boxes)
    {
        for (const SelectionBox& box : boxes) {
            _boxes.insert(box);
        }
    }

    // Accessors
    AMULET_CORE_DLLX const std::set<SelectionBox>& selection_boxes() const;

    // Bounds
    AMULET_CORE_DLLX std::int64_t min_x() const;
    AMULET_CORE_DLLX std::int64_t min_y() const;
    AMULET_CORE_DLLX std::int64_t min_z() const;
    AMULET_CORE_DLLX std::int64_t max_x() const;
    AMULET_CORE_DLLX std::int64_t max_y() const;
    AMULET_CORE_DLLX std::int64_t max_z() const;
    AMULET_CORE_DLLX std::tuple<std::int64_t, std::int64_t, std::int64_t> min() const;
    AMULET_CORE_DLLX std::tuple<std::int64_t, std::int64_t, std::int64_t> max() const;
    AMULET_CORE_DLLX std::pair<
        std::tuple<std::int64_t, std::int64_t, std::int64_t>,
        std::tuple<std::int64_t, std::int64_t, std::int64_t>>
    bounds() const;
    AMULET_CORE_DLLX SelectionBox bounding_box() const;

    // Contains and intersects
    AMULET_CORE_DLLX bool contains_block(std::int64_t x, std::int64_t y, std::int64_t z) const;
    AMULET_CORE_DLLX bool contains_point(double x, double y, double z) const;
    AMULET_CORE_DLLX bool intersects(const SelectionBox& other) const;
    AMULET_CORE_DLLX bool intersects(const SelectionGroup& other) const;

    // Transform
    AMULET_CORE_DLLX SelectionGroup translate(std::int64_t dx, std::int64_t dy, std::int64_t dz) const;

    // Operators
    AMULET_CORE_DLLX operator bool() const;
};

}
