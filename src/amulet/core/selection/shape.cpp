#include "shape.hpp"
#include "box_group.hpp"

namespace Amulet {

static std::list<SelectionShape::Deserialiser>& get_deserialisers()
{
    static std::list<SelectionShape::Deserialiser> deserialisers;
    return deserialisers;
}

std::unique_ptr<SelectionShape> SelectionShape::deserialise(std::string_view data, size_t& index)
{
    for (const auto& deserialiser : get_deserialisers()) {
        size_t index_temp = index;
        if (auto ptr = deserialiser(data, index_temp)) {
            index = index_temp;
            return ptr;
        }
    }
    throw std::runtime_error("Could not deserialise \"" + std::string(data) + "\"");
}
std::unique_ptr<SelectionShape> SelectionShape::deserialise(std::string_view s)
{
    size_t index = 0;
    return deserialise(s, index);
}

bool SelectionShape::register_deserialiser(
    std::function<
        std::unique_ptr<SelectionShape>(
            std::string_view, size_t&)>
        deserialiser)
{
    get_deserialisers().emplace_back(std::move(deserialiser));
    return true;
}

const Matrix4x4& SelectionShape::get_matrix() const
{
    return _matrix;
}

void SelectionShape::set_matrix(const Matrix4x4& matrix) {
    _matrix = matrix;
}

SelectionShape::operator SelectionBoxGroup() const
{
    return static_cast<std::set<SelectionBox>>(*this);
}

SelectionBoxGroup SelectionShape::voxelise() const
{
    return static_cast<SelectionBoxGroup>(*this);
}

} // namespace Amulet
