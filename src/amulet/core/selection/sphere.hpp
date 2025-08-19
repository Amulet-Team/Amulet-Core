#pragma once
#include <array>
#include <cstdint>

#include <amulet/core/dll.hpp>

#include "shape.hpp"

namespace Amulet {

class SelectionBox;

// The SelectionSphere class represents a single spherical selection.
class AMULET_CORE_EXPORT SelectionSphere : public SelectionShape {
private:
    double _x;
    double _y;
    double _z;
    double _radius;

public:
    SelectionSphere(
        double x,
        double y,
        double z,
        double radius)
        : _x(x)
        , _y(y)
        , _z(z)
        , _radius(radius)
    {
    }

    SelectionSphere(const SelectionSphere& other)
        : SelectionSphere(
              other._x,
              other._y,
              other._z,
              other._radius)
    {
    }

    // Accessors
    double get_x()
    {
        return _x;
    };
    double get_y()
    {
        return _y;
    };
    double get_z()
    {
        return _z;
    };
    double get_radius()
    {
        return _radius;
    };

    // SelectionShape
    std::unique_ptr<SelectionShape> copy() const override;
    std::set<SelectionBox> voxelise() const override;

    // Transform
    SelectionSphere translate_sphere(double dx, double dy, double dz) const;
    std::unique_ptr<SelectionShape> translate(double dx, double dy, double dz) const override;

    bool operator==(const SelectionSphere&) const;
    bool operator==(const SelectionShape&) const override;
};

} // namespace Amulet
