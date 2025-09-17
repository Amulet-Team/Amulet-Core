#include <cmath>
#include <iomanip>
#include <limits>
#include <sstream>
#include <string>

#include "box.hpp"
#include "ellipsoid.hpp"

namespace Amulet {

SelectionEllipsoid::SelectionEllipsoid()
    : SelectionShape()
{
}

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

std::string SelectionEllipsoid::serialise() const
{
    const auto& m1 = get_matrix();
    const auto& a = m1.data;
    auto [s, r, d] = m1.decompose();
    auto [sx, sy, sz] = s;
    auto [rx, ry, rz] = r;
    auto [dx, dy, dz] = d;
    auto m2 = Matrix4x4::transformation_matrix(sx, sy, sz, rx, ry, rz, dx, dy, dz);
    if (sx == sy && sy == sz && m1.almost_equal(m2)) {
        return "SelectionEllipsoid("
            + double_to_string(dx) + ","
            + double_to_string(dy) + ","
            + double_to_string(dz) + ","
            + double_to_string(sx / 2) + ")";
    } else {
        return "SelectionEllipsoid(Matrix4x4("
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

static const bool EllipsoidDeserialiserRegistered = SelectionShape::register_deserialiser(
    [](std::string_view data, size_t& index) -> std::unique_ptr<SelectionShape> {
        if (data.substr(index, 19) == "SelectionEllipsoid(") {
            index += 19;
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
                return std::make_unique<SelectionEllipsoid>(m);
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
                double radius = capture_number(data, index);
                skip_whitespace(data, index);
                skip_optional_character(data, index, ',');
                skip_whitespace(data, index);
                skip_character(data, index, ')');
                return std::make_unique<SelectionEllipsoid>(dx, dy, dz, radius);
            }
        }
        return nullptr;
    });

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

bool SelectionEllipsoid::operator==(const SelectionEllipsoid& other) const
{
    return get_matrix() == other.get_matrix();
}

bool SelectionEllipsoid::operator==(const SelectionShape& other) const
{
    if (const auto* ptr = dynamic_cast<const SelectionEllipsoid*>(&other)) {
        return *this == *ptr;
    }
    return false;
}

} // namespace Amulet
