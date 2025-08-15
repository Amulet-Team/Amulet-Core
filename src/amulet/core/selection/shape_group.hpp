#pragma once

#include <memory>
#include <vector>

#include <amulet/core/dll.hpp>

#include "shape.hpp"

namespace Amulet {

class SelectionBoxGroup;

class AMULET_CORE_EXPORT SelectionShapeGroup {
private:
    std::vector<std::unique_ptr<const SelectionShape>> _shapes;

public:
    // Default constructor
    SelectionShapeGroup() { };

    // Construct from a single shape
    SelectionShapeGroup(const SelectionShape& selection)
    {
        _shapes.push_back(selection.copy());
    }

    // Move vector constructor
    SelectionShapeGroup(std::vector<std::unique_ptr<const SelectionShape>>&& shapes)
        : _shapes(std::move(shapes))
    {
    }

    // Disable copying
    SelectionShapeGroup(const SelectionShapeGroup&) = delete;
    SelectionShapeGroup& operator=(const SelectionShapeGroup&) = delete;

    // Default move
    SelectionShapeGroup(SelectionShapeGroup&&) = default;
    SelectionShapeGroup& operator=(SelectionShapeGroup&&) = default;

    // Construct from an iterable of shapes
    template <typename Iterator>
        requires std::constructible_from<std::unique_ptr<SelectionShape>, std::iter_value_t<Iterator>>
    SelectionShapeGroup(const Iterator& begin, const Iterator& end)
    {
        for (auto it = begin(); it != end; it++) {
            _shapes.emplace_back(static_cast<std::unique_ptr<SelectionShape>>(*it));
        }
    }

    const std::vector<std::unique_ptr<const SelectionShape>>& get_shapes() const
    {
        return _shapes;
    }
    std::vector<std::unique_ptr<const SelectionShape>>::const_iterator begin() const
    {
        return _shapes.begin();
    }
    std::vector<std::unique_ptr<const SelectionShape>>::const_iterator end() const
    {
        return _shapes.end();
    }
    operator bool() const
    {
        return !_shapes.empty();
    }
    size_t count() const
    {
        return _shapes.size();
    }

    SelectionBoxGroup voxelise() const;

    explicit operator SelectionBoxGroup() const;
    explicit operator std::set<SelectionBox>() const;
};

}
