#include "shape_group.hpp"
#include "box.hpp"
#include "box_group.hpp"

namespace Amulet {

SelectionShapeGroup::SelectionShapeGroup() { }
SelectionShapeGroup::SelectionShapeGroup(std::vector<std::shared_ptr<SelectionShape>> shapes)
    : _shapes(std::move(shapes))
{
}

SelectionShapeGroup::SelectionShapeGroup(const SelectionShapeGroup& other) = default;
SelectionShapeGroup& SelectionShapeGroup::operator=(const SelectionShapeGroup& other) = default;
SelectionShapeGroup::SelectionShapeGroup(SelectionShapeGroup&&) = default;
SelectionShapeGroup& SelectionShapeGroup::operator=(SelectionShapeGroup&&) = default;

SelectionShapeGroup SelectionShapeGroup::deep_copy() const
{
    std::vector<std::shared_ptr<SelectionShape>> shapes;
    for (const auto& shape : get_shapes()) {
        shapes.push_back(shape->copy());
    }
    return shapes;
}

std::string SelectionShapeGroup::serialise() const
{
    std::string s = "SelectionShapeGroup([";
    for (const auto& shape : get_shapes()) {
        s += shape->serialise();
        s += ",";
    }
    s += "])";
    return s;
}

static void skip_whitespace(const std::string_view& data, size_t& index)
{
    while (index < data.size() && (data[index] == ' ' || data[index] == '\t' || data[index] == '\n' || data[index] == '\n')) {
        index++;
    }
    return;
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

SelectionShapeGroup SelectionShapeGroup::deserialise(std::string_view s)
{
    size_t index = 0;
    skip_whitespace(s, index);
    const std::string prefix = "SelectionShapeGroup([";
    if (s.substr(index, prefix.size()) != prefix) {
        throw std::runtime_error("Invalid serialised string. Expected \"SelectionShapeGroup(\"");
    }
    index += prefix.size();
    std::vector<std::shared_ptr<SelectionShape>> shapes;
    while (true) {
        skip_whitespace(s, index);
        if (s.size() <= index || s[index] == ']') {
            break;
        }
        shapes.push_back(SelectionShape::deserialise(s, index));
        skip_whitespace(s, index);
        if (s.size() <= index) {
            break;
        } else if (s[index] == ',') {
            index++;
        } else if (s[index] != ']') {
            throw std::runtime_error("Expected ',' or ']' after element at index " + std::to_string(index));
        }
    }
    skip_character(s, index, ']');
    skip_character(s, index, ')');
    return SelectionShapeGroup(std::move(shapes));
}

SelectionShapeGroup::operator std::set<SelectionBox>() const
{
    std::set<SelectionBox> boxes;
    for (const auto& shape : _shapes) {
        auto shape_boxes = static_cast<std::set<SelectionBox>>(*shape);
        boxes.insert(shape_boxes.begin(), shape_boxes.end());
    }
    return boxes;
}

SelectionShapeGroup::operator SelectionBoxGroup() const
{
    return static_cast<std::set<SelectionBox>>(*this);
}

SelectionBoxGroup SelectionShapeGroup::voxelise() const
{
    return static_cast<SelectionBoxGroup>(*this);
}

bool SelectionShapeGroup::almost_equal(const SelectionShapeGroup& other) const
{
    if (count() != other.count()) {
        return false;
    }
    auto& shapes1 = get_shapes();
    auto& shapes2 = other.get_shapes();
    for (size_t i = 0; i < shapes1.size(); i++) {
        if (!shapes1[i]->almost_equal(*shapes2[i])) {
            return false;
        }
    }
    return true;
}

bool SelectionShapeGroup::operator == (const SelectionShapeGroup& other) const
{
    if (count() != other.count()) {
        return false;
    }
    const auto& shapes = get_shapes();
    const auto& other_shapes = other.get_shapes();
    for (size_t i = 0; i < shapes.size(); i++) {
        if (*shapes[i] != *other_shapes[i]) {
            return false;
        }
    }
    return true;
}

} // namespace Amulet
