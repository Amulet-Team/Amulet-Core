#include <cmath>
#include <iomanip>
#include <limits>
#include <sstream>

#include <numbers>

#include "box.hpp"
#include "cuboid.hpp"

namespace Amulet {

SelectionCuboid::SelectionCuboid()
    : SelectionShape()
{
}

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

static std::string double_to_string(double v)
{
    std::ostringstream oss;
    oss << std::setprecision(8) << std::fixed << v;
    auto s = oss.str();
    size_t end = s.size() - 1;
    while (s[end] == '0') {
        end--;
    }
    if (s[end] == '.') {
        end--;
    }
    return s.substr(0, end + 1);
}

std::string SelectionCuboid::serialise() const
{
    const auto& m1 = get_matrix();
    const auto& a = m1.data;
    auto [s, r, d] = m1.decompose();
    auto [sx, sy, sz] = s;
    auto [rx, ry, rz] = r;
    auto [dx, dy, dz] = d;
    auto m2 = Matrix4x4::transformation_matrix(sx, sy, sz, rx, ry, rz, dx, dy, dz);
    if (m1.almost_equal(m2)) {
        if (rx == 0 && ry == 0 && rz == 0) {
            return "SelectionCuboid("
                + double_to_string(dx) + ","
                + double_to_string(dy) + ","
                + double_to_string(dz) + ","
                + double_to_string(sx) + ","
                + double_to_string(sy) + ","
                + double_to_string(sz) + ")";
        } else {
            return "SelectionCuboid(Matrix4x4::transformation_matrix("
                + double_to_string(sx) + ","
                + double_to_string(sy) + ","
                + double_to_string(sz) + ","
                + double_to_string(rx) + ","
                + double_to_string(ry) + ","
                + double_to_string(rz) + ","
                + double_to_string(dx) + ","
                + double_to_string(dy) + ","
                + double_to_string(dz) + "))";
        }
    } else {
        return "SelectionCuboid(Matrix4x4("
            + double_to_string(a[0][0]) + ","
            + double_to_string(a[0][1]) + ","
            + double_to_string(a[0][2]) + ","
            + double_to_string(a[0][3]) + ","
            + double_to_string(a[1][0]) + ","
            + double_to_string(a[1][1]) + ","
            + double_to_string(a[1][2]) + ","
            + double_to_string(a[1][3]) + ","
            + double_to_string(a[2][0]) + ","
            + double_to_string(a[2][1]) + ","
            + double_to_string(a[2][2]) + ","
            + double_to_string(a[2][3]) + ","
            + double_to_string(a[3][0]) + ","
            + double_to_string(a[3][1]) + ","
            + double_to_string(a[3][2]) + ","
            + double_to_string(a[3][3]) + "))";
    }
}

static void skip_whitespace(const std::string_view& data, size_t& index)
{
    while (index < data.size() && (data[index] == ' ' || data[index] == '\t' || data[index] == '\n' || data[index] == '\n')) {
        index++;
    }
    return;
}

static double capture_number(const std::string_view& data, size_t& index)
{
    size_t start = index;
    bool has_decimal = false;
    for (; index < data.size(); index++) {
        switch (data[index]) {
        case '-':
        case '+':
            if (start != index) {
                throw std::runtime_error("- and + can only appear at the start of a number. Index " + std::to_string(start));
            }
            break;
        case '0':
        case '1':
        case '2':
        case '3':
        case '4':
        case '5':
        case '6':
        case '7':
        case '8':
        case '9':
            break;
        case '.':
            if (has_decimal) {
                throw std::runtime_error("Numbers can only have on decimal point. Index " + std::to_string(start));
            } else {
                has_decimal = true;
            }
            break;
        default:
            if (start == index) {
                throw std::runtime_error("No number found. Index " + std::to_string(start));
            }
            return std::stod(std::string(data.substr(start, index - start)));
        }
    }
    if (start == index) {
        throw std::runtime_error("No number found. Index " + std::to_string(start));
    }
    return std::stod(std::string(data.substr(start, index - start)));
}

static void skip_character(const std::string_view& data, size_t& index, char c)
{
    if (index < data.size() && data[index] == c) {
        index++;
    } else {
        throw std::runtime_error("Expected character " + std::string(1, c) + " at index " + std::to_string(index));
    }
}

static void skip_optional_character(const std::string_view& data, size_t& index, char c)
{
    if (index < data.size() && data[index] == c) {
        index++;
    }
}

static const bool CuboidDeserialiserRegistered = SelectionShape::register_deserialiser(
    [](std::string_view data, size_t& index) -> std::unique_ptr<SelectionShape> {
        if (data.substr(index, 16) == "SelectionCuboid(") {
            index += 16;
            skip_whitespace(data, index);
            if (data.substr(index, 10) == "Matrix4x4(") {
                index += 10;
                skip_whitespace(data, index);
                Matrix4x4 m;
                for (auto i = 0; i < 4; i++) {
                    for (auto j = 0; j < 4; j++) {
                        m.data[i][j] = capture_number(data, index);
                        skip_whitespace(data, index);
                        if (i == 3 && j == 3) {
                            skip_optional_character(data, index, ',');
                        } else {
                            skip_character(data, index, ',');
                        }
                        skip_whitespace(data, index);
                    }
                }
                skip_character(data, index, ')');
                skip_character(data, index, ')');
                return std::make_unique<SelectionCuboid>(m);
            } else if (data.substr(index, 33) == "Matrix4x4::transformation_matrix(") {
                index += 33;
                skip_whitespace(data, index);
                double sx = capture_number(data, index);
                skip_whitespace(data, index);
                skip_character(data, index, ',');
                skip_whitespace(data, index);
                double sy = capture_number(data, index);
                skip_whitespace(data, index);
                skip_character(data, index, ',');
                skip_whitespace(data, index);
                double sz = capture_number(data, index);
                skip_whitespace(data, index);
                skip_character(data, index, ',');
                skip_whitespace(data, index);
                double rx = capture_number(data, index);
                skip_whitespace(data, index);
                skip_character(data, index, ',');
                skip_whitespace(data, index);
                double ry = capture_number(data, index);
                skip_whitespace(data, index);
                skip_character(data, index, ',');
                skip_whitespace(data, index);
                double rz = capture_number(data, index);
                skip_whitespace(data, index);
                skip_character(data, index, ',');
                skip_whitespace(data, index);
                double dx = capture_number(data, index);
                skip_whitespace(data, index);
                skip_character(data, index, ',');
                skip_whitespace(data, index);
                double dy = capture_number(data, index);
                skip_whitespace(data, index);
                skip_character(data, index, ',');
                skip_whitespace(data, index);
                double dz = capture_number(data, index);
                skip_whitespace(data, index);
                skip_optional_character(data, index, ',');
                skip_whitespace(data, index);
                skip_character(data, index, ')');
                skip_character(data, index, ')');
                return std::make_unique<SelectionCuboid>(
                    Matrix4x4::transformation_matrix(
                        sx, sy, sz, rx, ry, rz, dx, dy, dz));
            } else {
                double dx = capture_number(data, index);
                skip_whitespace(data, index);
                skip_character(data, index, ',');
                skip_whitespace(data, index);
                double dy = capture_number(data, index);
                skip_whitespace(data, index);
                skip_character(data, index, ',');
                skip_whitespace(data, index);
                double dz = capture_number(data, index);
                skip_whitespace(data, index);
                skip_character(data, index, ',');
                skip_whitespace(data, index);
                double sx = capture_number(data, index);
                skip_whitespace(data, index);
                skip_character(data, index, ',');
                skip_whitespace(data, index);
                double sy = capture_number(data, index);
                skip_whitespace(data, index);
                skip_character(data, index, ',');
                skip_whitespace(data, index);
                double sz = capture_number(data, index);
                skip_whitespace(data, index);
                skip_optional_character(data, index, ',');
                skip_whitespace(data, index);
                skip_character(data, index, ')');
                return std::make_unique<SelectionCuboid>(dx, dy, dz, sx, sy, sz);
            }
        }
        return nullptr;
    });

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

bool SelectionCuboid::operator==(const SelectionCuboid& other) const
{
    return get_matrix() == other.get_matrix();
}

bool SelectionCuboid::operator==(const SelectionShape& other) const
{
    if (const auto* ptr = dynamic_cast<const SelectionCuboid*>(&other)) {
        return *this == *ptr;
    }
    return false;
}

} // namespace Amulet
