#pragma once

#include <amulet/core/dll.hpp>

#include "shape.hpp"

namespace Amulet {

class AMULET_CORE_EXPORT SelectionCuboid : public SelectionShape {
public:
    SelectionCuboid();
    SelectionCuboid(const Matrix4x4&);

    SelectionCuboid(
        double min_x,
        double min_y,
        double min_z,
        double size_x,
        double size_y,
        double size_z
    );

    SelectionCuboid(const SelectionCuboid& other);

    std::string serialise() const override;

    std::unique_ptr<SelectionShape> copy() const override;
    explicit operator std::set<SelectionBox>() const override;

    // Transform
    SelectionCuboid translate_cuboid(double dx, double dy, double dz) const;
    SelectionCuboid transform_cuboid(const Matrix4x4&) const;
    std::unique_ptr<SelectionShape> transform(const Matrix4x4&) const override;

    bool almost_equal(const SelectionCuboid&) const;
    bool almost_equal(const SelectionShape&) const override;
    bool operator==(const SelectionCuboid&) const;
    bool operator==(const SelectionShape&) const override;
};

} // namespace Amulet
