#pragma once

#include <memory>
#include <set>

#include <amulet/core/dll.hpp>

namespace Amulet {

class SelectionBox;

class AMULET_CORE_EXPORT SelectionShape {
public:
    virtual ~SelectionShape() = default;

    // Convert the shape into unit voxels.
    virtual std::set<SelectionBox> voxelise() const = 0;

    explicit operator std::set<SelectionBox>() const
    {
        return voxelise();
    }

    // Create a copy of the class.
    virtual std::unique_ptr<SelectionShape> copy() const = 0;

    explicit operator std::unique_ptr<SelectionShape>() const {
        return copy();
    }
};

} // namespace Amulet
