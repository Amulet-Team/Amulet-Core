#pragma once

#include <array>
#include <concepts>
#include <ranges>
#include <set>

#include <amulet/core/dll.hpp>

#include "box.hpp"

namespace Amulet {

class SelectionBox;

class SelectionGroup {
private:
    std::set<SelectionBox> _boxes;

public:
    // Constructors
    SelectionGroup() {};
    SelectionGroup(const SelectionBox& box)
    {
        _boxes.insert(box);
    }

    template <typename Iterable>
        requires std::ranges::input_range<Iterable> && std::convertible_to<std::ranges::range_value_t<Iterable>, const SelectionBox&>
    SelectionGroup(const Iterable& boxes)
    {
        for (const SelectionBox& box : boxes) {
            _boxes.emplace(box);
        }
    }

    // Accessors
    const std::set<SelectionBox>& selection_boxes() const
    {
        return _boxes;
    }
    size_t size() const
    {
        return _boxes.size();
    }

    // Bounds
    AMULET_CORE_EXPORT std::int64_t min_x() const;
    AMULET_CORE_EXPORT std::int64_t min_y() const;
    AMULET_CORE_EXPORT std::int64_t min_z() const;
    AMULET_CORE_EXPORT std::int64_t max_x() const;
    AMULET_CORE_EXPORT std::int64_t max_y() const;
    AMULET_CORE_EXPORT std::int64_t max_z() const;
    AMULET_CORE_EXPORT std::array<std::int64_t, 3> min() const;
    AMULET_CORE_EXPORT std::array<std::int64_t, 3> max() const;
    AMULET_CORE_EXPORT std::pair<
        std::array<std::int64_t, 3>,
        std::array<std::int64_t, 3>>
    bounds() const;
    AMULET_CORE_EXPORT SelectionBox bounding_box() const;

    // Contains and intersects
    AMULET_CORE_EXPORT bool contains_block(std::int64_t x, std::int64_t y, std::int64_t z) const;
    AMULET_CORE_EXPORT bool contains_point(double x, double y, double z) const;
    AMULET_CORE_EXPORT bool intersects(const SelectionBox& other) const;
    AMULET_CORE_EXPORT bool intersects(const SelectionGroup& other) const;

    // Transform
    AMULET_CORE_EXPORT SelectionGroup translate(std::int64_t dx, std::int64_t dy, std::int64_t dz) const;

    // Operators
    operator bool() const
    {
        return !_boxes.empty();
    }
    bool operator==(const SelectionGroup& rhs) const = default;
    bool operator!=(const SelectionGroup& rhs) const = default;
};

}
