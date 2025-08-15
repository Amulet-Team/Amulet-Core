#pragma once

#include <array>
#include <concepts>
#include <ranges>
#include <set>

#include <amulet/core/dll.hpp>

#include "box.hpp"

namespace Amulet {


class AMULET_CORE_EXPORT SelectionBoxes {
private:
    std::set<SelectionBox> _boxes;

public:
    // Constructors
    SelectionBoxes() {};
    SelectionBoxes(const SelectionBox& box)
    {
        _boxes.insert(box);
    }

    template <typename Iterable>
        requires std::ranges::input_range<Iterable> && std::convertible_to<std::ranges::range_value_t<Iterable>, const SelectionBox&>
    SelectionBoxes(const Iterable& boxes)
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
    [[deprecated("Use count instead.")]]
    size_t size() const
    {
        return _boxes.size();
    }
    size_t count() const
    {
        return _boxes.size();
    }

    // Bounds
    std::int64_t min_x() const;
    std::int64_t min_y() const;
    std::int64_t min_z() const;
    std::int64_t max_x() const;
    std::int64_t max_y() const;
    std::int64_t max_z() const;
    std::array<std::int64_t, 3> min() const;
    std::array<std::int64_t, 3> max() const;
    std::pair<
        std::array<std::int64_t, 3>,
        std::array<std::int64_t, 3>>
    bounds() const;
    SelectionBox bounding_box() const;

    // Contains and intersects
    bool contains_block(std::int64_t x, std::int64_t y, std::int64_t z) const;
    bool contains_point(double x, double y, double z) const;
    bool intersects(const SelectionBox& other) const;
    bool intersects(const SelectionBoxes& other) const;

    // Transform
    SelectionBoxes translate(std::int64_t dx, std::int64_t dy, std::int64_t dz) const;

    // Operators
    operator bool() const
    {
        return !_boxes.empty();
    }
    bool operator==(const SelectionBoxes& rhs) const = default;
    bool operator!=(const SelectionBoxes& rhs) const = default;
};

}
