#pragma once

#include <memory>
#include <string>
#include <string_view>
#include <vector>

#include <amulet/core/dll.hpp>

#include "shape.hpp"

namespace Amulet {

class SelectionBox;
class SelectionBoxGroup;

class AMULET_CORE_EXPORT SelectionShapeGroup {
private:
    std::vector<std::shared_ptr<SelectionShape>> _shapes;

public:
    SelectionShapeGroup();
    SelectionShapeGroup(std::vector<std::shared_ptr<SelectionShape>> shapes);

    SelectionShapeGroup(const SelectionShapeGroup&);
    SelectionShapeGroup& operator=(const SelectionShapeGroup&);

    SelectionShapeGroup(SelectionShapeGroup&&);
    SelectionShapeGroup& operator=(SelectionShapeGroup&&);

    SelectionShapeGroup deep_copy() const;

    std::string serialise() const;
    static SelectionShapeGroup deserialise(std::string_view);

    const std::vector<std::shared_ptr<SelectionShape>>& get_shapes() const
    {
        return _shapes;
    }
    std::vector<std::shared_ptr<SelectionShape>>& get_shapes()
    {
        return _shapes;
    }
    void set_shapes(std::vector<std::shared_ptr<SelectionShape>> shapes)
    {
        _shapes = std::move(shapes);
    }
    std::vector<std::shared_ptr<SelectionShape>>::const_iterator begin() const
    {
        return _shapes.begin();
    }
    std::vector<std::shared_ptr<SelectionShape>>::const_iterator end() const
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

    bool almost_equal(const SelectionShapeGroup&) const;
    bool operator==(const SelectionShapeGroup&) const;
};

}
