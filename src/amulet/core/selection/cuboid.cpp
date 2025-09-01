#include <cmath>
#include <limits>

#include <numbers>

#include "box.hpp"
#include "cuboid.hpp"

namespace Amulet {

SelectionCuboid::SelectionCuboid(const Matrix4x4& matrix)
    : SelectionShape(matrix)
{
}

SelectionCuboid::SelectionCuboid(
    double min_x,
    double min_y,
    double min_z,
    double size_x,
    double size_y,
    double size_z)
    : SelectionShape(
          Matrix4x4::scale_matrix(std::abs(size_x), std::abs(size_y), std::abs(size_z))
              .translate(min_x, min_y, min_z))
{
}

SelectionCuboid::SelectionCuboid(const SelectionCuboid& other)
    : SelectionShape(other.get_matrix())
{
}

std::unique_ptr<SelectionShape> SelectionCuboid::copy() const
{
    return std::make_unique<SelectionCuboid>(*this);
}

static const std::vector<std::array<double, 3>> SelectionCuboidBoundingBox {
    { 0, 0, 0 },
    { 0, 0, 1 },
    { 0, 1, 0 },
    { 0, 1, 1 },
    { 1, 0, 0 },
    { 1, 0, 1 },
    { 1, 1, 0 },
    { 1, 1, 1 }
};

static const double half_pi = std::numbers::pi / 2;

static bool almost_90(double angle)
{
    // Find the nearest multiple of 90 degrees
    double nearest = std::round(angle / half_pi) * half_pi;
    // Return if the difference is less than an error threshold
    return std::abs(angle - nearest) < 0.00001;
}

SelectionCuboid::operator std::set<SelectionBox>() const
{
    const auto& matrix = get_matrix();
    // Find the transformed bounding box
    auto bounding_points = matrix * SelectionCuboidBoundingBox;
    double min_tx = std::numeric_limits<double>::max();
    double min_ty = std::numeric_limits<double>::max();
    double min_tz = std::numeric_limits<double>::max();
    double max_tx = std::numeric_limits<double>::lowest();
    double max_ty = std::numeric_limits<double>::lowest();
    double max_tz = std::numeric_limits<double>::lowest();

    for (auto& [tx, ty, tz] : bounding_points) {
        min_tx = std::min(min_tx, tx);
        min_ty = std::min(min_ty, ty);
        min_tz = std::min(min_tz, tz);
        max_tx = std::max(max_tx, tx);
        max_ty = std::max(max_ty, ty);
        max_tz = std::max(max_tz, tz);
    }

    min_tx = std::round(min_tx);
    min_ty = std::round(min_ty);
    min_tz = std::round(min_tz);
    max_tx = std::round(max_tx);
    max_ty = std::round(max_ty);
    max_tz = std::round(max_tz);

    std::set<SelectionBox> boxes;

    // If all rotations are a multiple of 90 degrees and
    // there is no complex scaling we can return one box.
    auto [scale, rotation, displacement] = matrix.decompose();
    if (
        almost_90(std::get<0>(rotation))
        && almost_90(std::get<1>(rotation))
        && almost_90(std::get<2>(rotation))
        && matrix.almost_equal(
            Matrix4x4::transformation_matrix(
                std::get<0>(scale),
                std::get<1>(scale),
                std::get<2>(scale),
                std::get<0>(rotation),
                std::get<1>(rotation),
                std::get<2>(rotation),
                std::get<0>(displacement),
                std::get<1>(displacement),
                std::get<2>(displacement)))) {
        boxes.emplace(
            static_cast<std::int64_t>(min_tx),
            static_cast<std::int64_t>(min_ty),
            static_cast<std::int64_t>(min_tz),
            static_cast<size_t>(std::ceil(max_tx - min_tx)),
            static_cast<size_t>(std::ceil(max_ty - min_ty)),
            static_cast<size_t>(std::ceil(max_tz - min_tz)));
        return boxes;
    }

    Matrix4x4 inverse;
    try {
        inverse = matrix.inverse();
    } catch (const std::runtime_error&) {
        return boxes;
    }

    auto y_steps = static_cast<size_t>(std::round(max_ty - min_ty));
    std::vector<std::array<double, 3>> transformed_points(y_steps);

    // Iterate through every column in the transformed bounding box.
    // TODO: optimise this. A lot of these may miss.
    // TODO: This could be implemented using ray casting.
    for (auto tx = min_tx + 0.5; tx < max_tx; tx++) {
        for (auto tz = min_tz + 0.5; tz < max_tz; tz++) {
            for (size_t dy = 0; dy < y_steps; dy++) {
                transformed_points[dy][0] = tx;
                transformed_points[dy][1] = min_ty + 0.5 + dy;
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
                if (0.0 <= x && x <= 1.0 && 0.0 <= y && y <= 1.0 && 0.0 <= z && z <= 1.0) {
                    // Point is in the cuboid
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
                    // Found a point outside the cuboid. Break out of the loop.
                    break;
                }
            }
            if (hit) {
                // We should have the first and last points in the cuboid
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

SelectionCuboid SelectionCuboid::translate_cuboid(double dx, double dy, double dz) const
{
    return SelectionCuboid(get_matrix().translate(dx, dy, dz));
}
SelectionCuboid SelectionCuboid::transform_cuboid(const Matrix4x4& m) const
{
    return SelectionCuboid(m * get_matrix());
}
std::unique_ptr<SelectionShape> SelectionCuboid::transform(const Matrix4x4& m) const
{
    return std::make_unique<SelectionCuboid>(transform_cuboid(m));
}

bool SelectionCuboid::almost_equal(const SelectionCuboid& other) const
{
    return get_matrix().almost_equal(other.get_matrix());
}

bool SelectionCuboid::almost_equal(const SelectionShape& other) const
{
    if (const auto* ptr = dynamic_cast<const SelectionCuboid*>(&other)) {
        return almost_equal(*ptr);
    }
    return false;
}

} // namespace Amulet
