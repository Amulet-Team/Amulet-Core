#pragma once

#include <array>
#include <concepts>
#include <ranges>
#include <set>

#include <amulet/core/dll.hpp>

#include "box.hpp"

namespace Amulet {

class AMULET_CORE_EXPORT SelectionBoxGroup {
private:
    std::set<SelectionBox> _boxes;

public:
    // Forwarding constructor
    template <typename... Args>
    SelectionBoxGroup(Args&&... args)
        : _boxes(std::forward<Args>(args)...)
    {
    }

    SelectionBoxGroup(std::initializer_list<SelectionBox> boxes)
        : _boxes(boxes)
    {
    }

    // Accessors
    const std::set<SelectionBox>& get_boxes() const
    {
        return _boxes;
    }
    size_t count() const
    {
        return _boxes.size();
    }
    std::set<SelectionBox>::const_iterator begin() const
    {
        return _boxes.begin();
    }
    std::set<SelectionBox>::const_iterator end() const
    {
        return _boxes.end();
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
    bool intersects(const SelectionBoxGroup& other) const;

    // Transform
    SelectionBoxGroup translate(std::int64_t dx, std::int64_t dy, std::int64_t dz) const;
    SelectionBoxGroup transform(const Matrix4x4&) const;

    // Operators
    operator bool() const
    {
        return !_boxes.empty();
    }
    std::strong_ordering operator<=>(const SelectionBoxGroup& other) const = default;
    bool operator==(const SelectionBoxGroup& rhs) const = default;
    bool operator!=(const SelectionBoxGroup& rhs) const = default;

    operator std::set<SelectionBox>() const
    {
        return _boxes;
    }
};

}
