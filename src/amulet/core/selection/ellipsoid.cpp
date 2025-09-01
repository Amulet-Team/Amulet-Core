#include <cmath>
#include <limits>

#include "box.hpp"
#include "ellipsoid.hpp"

namespace Amulet {

SelectionEllipsoid::SelectionEllipsoid(const Matrix4x4& matrix)
    : SelectionShape(matrix)
{
}

SelectionEllipsoid::SelectionEllipsoid(
    double x,
    double y,
    double z,
    double radius)
    : SelectionShape(
          Matrix4x4::scale_matrix(2.0 * radius, 2.0 * radius, 2.0 * radius)
              .translate(x, y, z))
{
}

SelectionEllipsoid::SelectionEllipsoid(const SelectionEllipsoid& other)
    : SelectionShape(other.get_matrix())
{
}

std::unique_ptr<SelectionShape> SelectionEllipsoid::copy() const
{
    return std::make_unique<SelectionEllipsoid>(*this);
}

static const std::vector<std::array<double, 3>> SelectionEllipsoidBoundingBox {
    { -0.5, -0.5, -0.5 },
    { -0.5, -0.5, 0.5 },
    { -0.5, 0.5, -0.5 },
    { -0.5, 0.5, 0.5 },
    { 0.5, -0.5, -0.5 },
    { 0.5, -0.5, 0.5 },
    { 0.5, 0.5, -0.5 },
    { 0.5, 0.5, 0.5 },
};

SelectionEllipsoid::operator std::set<SelectionBox>() const
{
    const auto& matrix = get_matrix();
    // Find the transformed bounding box
    auto bounding_points = matrix * SelectionEllipsoidBoundingBox;
    double min_tx = std::numeric_limits<double>::max();
    double min_ty = std::numeric_limits<double>::max();
    double min_tz = std::numeric_limits<double>::max();
    double max_tx = std::numeric_limits<double>::min();
    double max_ty = std::numeric_limits<double>::min();
    double max_tz = std::numeric_limits<double>::min();

    for (auto& [tx, ty, tz] : bounding_points) {
        min_tx = std::min(min_tx, tx);
        min_ty = std::min(min_ty, ty);
        min_tz = std::min(min_tz, tz);
        max_tx = std::max(max_tx, tx);
        max_ty = std::max(max_ty, ty);
        max_tz = std::max(max_tz, tz);
    }

    min_tx = std::round(min_tx) + 0.5;
    min_ty = std::round(min_ty) + 0.5;
    min_tz = std::round(min_tz) + 0.5;

    std::set<SelectionBox> boxes;

    Matrix4x4 inverse;
    try {
        inverse = matrix.inverse();
    } catch (const std::runtime_error&) {
        return boxes;
    }

    auto y_steps = static_cast<size_t>(std::ceil(max_ty - min_ty));
    std::vector<std::array<double, 3>> transformed_points(y_steps);

    // Iterate through every column in the transformed bounding box.
    // TODO: optimise this. A lot of these may miss.
    // TODO: This could be implemented using ray casting.
    for (auto tx = min_tx; tx < max_tx; tx++) {
        for (auto tz = min_tz; tz < max_tz; tz++) {
            for (size_t dy = 0; dy < y_steps; dy++) {
                transformed_points[dy][0] = tx;
                transformed_points[dy][1] = min_ty + dy;
                transformed_points[dy][2] = tz;
            }
            // Transform the points to the original space
            auto original_points = inverse * transformed_points;
            bool hit = false;
            size_t first = 0;
            size_t last = 0;
            // Iterate through the points to find the first and last intersection
            for (size_t dy = 0; dy < y_steps; dy++) {
                auto& [x, y, z] = original_points[dy];
                if (std::pow(x, 2) + std::pow(y, 2) + std::pow(z, 2) <= 0.25) {
                    // Point is in the sphere
                    if (hit) {
                        // Update the end position
                        last = dy;
                    } else {
                        // Set the start position
                        hit = true;
                        first = dy;
                        last = dy;
                    }
                } else if (hit) {
                    // Found a point outside the sphere. Break out of the loop.
                    break;
                }
            }
            if (hit) {
                // We should have the first and last points in the sphere
                auto box_min_y = static_cast<std::int64_t>(std::floor(transformed_points[first][1]));
                auto box_max_y = static_cast<std::int64_t>(std::floor(transformed_points[last][1])) + 1;
                boxes.emplace(
                    static_cast<std::int64_t>(std::floor(tx)),
                    box_min_y,
                    static_cast<std::int64_t>(std::floor(tz)),
                    1,
                    box_max_y - box_min_y,
                    1);
            }
        }
    }
    return boxes;
}

SelectionEllipsoid SelectionEllipsoid::translate_ellipsoid(double dx, double dy, double dz) const
{
    return SelectionEllipsoid(get_matrix().translate(dx, dy, dz));
}
SelectionEllipsoid SelectionEllipsoid::transform_ellipsoid(const Matrix4x4& m) const
{
    return SelectionEllipsoid(m * get_matrix());
}
std::unique_ptr<SelectionShape> SelectionEllipsoid::transform(const Matrix4x4& m) const
{
    return std::make_unique<SelectionEllipsoid>(transform_ellipsoid(m));
}

bool SelectionEllipsoid::almost_equal(const SelectionEllipsoid& other) const
{
    return get_matrix().almost_equal(other.get_matrix());
}

bool SelectionEllipsoid::almost_equal(const SelectionShape& other) const
{
    if (const auto* ptr = dynamic_cast<const SelectionEllipsoid*>(&other)) {
        return almost_equal(*ptr);
    }
    return false;
}

} // namespace Amulet
