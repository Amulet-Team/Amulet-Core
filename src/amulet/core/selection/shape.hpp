#pragma once

#include <memory>
#include <set>

#include <amulet/utils/matrix.hpp>

#include <amulet/core/dll.hpp>

namespace Amulet {

class SelectionBox;
class SelectionBoxGroup;

class AMULET_CORE_EXPORT SelectionShape {
private:
    Matrix4x4 _matrix;
public:

    SelectionShape() = default;
    SelectionShape(const Matrix4x4& matrix)
        : _matrix(matrix)
    {
    }
    virtual ~SelectionShape() = default;

    const Matrix4x4& get_matrix() const;

    // Create a copy of the class.
    virtual std::unique_ptr<SelectionShape> copy() const = 0;

    explicit operator std::unique_ptr<SelectionShape>() const
    {
        return copy();
    }

    // Convert the shape into unit voxels.
    virtual explicit operator std::set<SelectionBox>() const = 0;
    explicit operator SelectionBoxGroup() const;
    SelectionBoxGroup voxelise() const;

    // translate and transform
    virtual std::unique_ptr<SelectionShape> transform(const Matrix4x4&) const = 0;
    std::unique_ptr<SelectionShape> translate(double dx, double dy, double dz) const
    {
        return transform(Matrix4x4::translation_matrix(dx, dy, dz));
    }

    // Equality
    virtual bool almost_equal(const SelectionShape&) const = 0;
};

} // namespace Amulet
