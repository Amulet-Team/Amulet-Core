#pragma once

#include <memory>
#include <vector>

#include <amulet/core/dll.hpp>

#include "shape.hpp"

namespace Amulet {

class SelectionBox;
class SelectionBoxGroup;

class AMULET_CORE_EXPORT SelectionShapeGroup {
private:
    std::vector<std::unique_ptr<const SelectionShape>> _shapes;

public:
    // Forwarding constructor
    template <typename... Args>
    SelectionShapeGroup(Args&&... args)
        : _shapes(std::forward<Args>(args)...)
    {
    }

    // Disable copying
    SelectionShapeGroup(const SelectionShapeGroup&) = delete;
    SelectionShapeGroup& operator=(const SelectionShapeGroup&) = delete;

    // Default move
    SelectionShapeGroup(SelectionShapeGroup&&) = default;
    SelectionShapeGroup& operator=(SelectionShapeGroup&&) = default;

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

    explicit operator SelectionBoxGroup() const;
    explicit operator std::set<SelectionBox>() const;
    SelectionBoxGroup voxelise() const;
};

}
