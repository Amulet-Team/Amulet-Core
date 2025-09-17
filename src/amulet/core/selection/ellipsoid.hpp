#pragma once
#include <cstdint>

#include <amulet/core/dll.hpp>

#include "shape.hpp"

namespace Amulet {

class SelectionBox;

// The SelectionEllipsoid class represents a single spherical selection.
class AMULET_CORE_EXPORT SelectionEllipsoid : public SelectionShape {
public:
    SelectionEllipsoid();
    SelectionEllipsoid(const Matrix4x4&);

    SelectionEllipsoid(
        double x,
        double y,
        double z,
        double radius);
        
    SelectionEllipsoid(const SelectionEllipsoid& other);

    std::string serialise() const override;
        
    std::unique_ptr<SelectionShape> copy() const override;
    explicit operator std::set<SelectionBox>() const override;

    // Transform
    SelectionEllipsoid translate_ellipsoid(double dx, double dy, double dz) const;
    SelectionEllipsoid transform_ellipsoid(const Matrix4x4&) const;
    std::unique_ptr<SelectionShape> transform(const Matrix4x4&) const override;

    bool almost_equal(const SelectionEllipsoid&) const;
    bool almost_equal(const SelectionShape&) const override;
    bool operator==(const SelectionEllipsoid&) const;
    bool operator==(const SelectionShape&) const override;
};

} // namespace Amulet
