#pragma once

#include <array>
#include <concepts>
#include <ranges>
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
        requires std::ranges::input_range<Iterable> && std::convertible_to<std::ranges::range_value_t<Iterable>, const SelectionBox&>
    SelectionGroup(const Iterable& boxes)
    {
        for (const SelectionBox& box : boxes) {
            _boxes.emplace(box);
        }
    }

    // Accessors
    AMULET_CORE_DLLX const std::set<SelectionBox>& selection_boxes() const;
    AMULET_CORE_DLLX size_t size() const;

    // Bounds
    AMULET_CORE_DLLX std::int64_t min_x() const;
    AMULET_CORE_DLLX std::int64_t min_y() const;
    AMULET_CORE_DLLX std::int64_t min_z() const;
    AMULET_CORE_DLLX std::int64_t max_x() const;
    AMULET_CORE_DLLX std::int64_t max_y() const;
    AMULET_CORE_DLLX std::int64_t max_z() const;
    AMULET_CORE_DLLX std::array<std::int64_t, 3> min() const;
    AMULET_CORE_DLLX std::array<std::int64_t, 3> max() const;
    AMULET_CORE_DLLX std::pair<
        std::array<std::int64_t, 3>,
        std::array<std::int64_t, 3>>
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
    bool operator==(const SelectionGroup& rhs) const = default;
    bool operator!=(const SelectionGroup& rhs) const = default;
};

}
