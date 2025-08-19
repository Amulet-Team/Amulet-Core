#pragma once

#include <memory>
#include <set>

#include <amulet/core/dll.hpp>

namespace Amulet {

class SelectionBox;

class AMULET_CORE_EXPORT SelectionShape {
public:
    virtual ~SelectionShape() = default;

    // Create a copy of the class.
    virtual std::unique_ptr<SelectionShape> copy() const = 0;

    explicit operator std::unique_ptr<SelectionShape>() const
    {
        return copy();
    }

    // Convert the shape into unit voxels.
    virtual std::set<SelectionBox> voxelise() const = 0;

    explicit operator std::set<SelectionBox>() const
    {
        return voxelise();
    }

    // translate and transform
    virtual std::unique_ptr<SelectionShape> translate(double dx, double dy, double dz) const = 0;

    // Equality
    virtual bool operator==(const SelectionShape&) const = 0;
};

} // namespace Amulet
