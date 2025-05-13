#include <amulet/core/dll.hpp>

#include "biome_3d_component.hpp"

namespace Amulet {

// Biome3DComponent

std::optional<std::string> Biome3DComponent::serialise() const
{
    throw std::runtime_error("NotImplementedError");
}
// Deserialise the component
void Biome3DComponent::deserialise(std::optional<std::string>)
{
    throw std::runtime_error("NotImplementedError");
}

const std::string Biome3DComponent::ComponentID = "Amulet::Biome3DComponent";

std::shared_ptr<Biome3DComponentData> Biome3DComponent::get_biome()
{
    if (_value) {
        return *_value;
    }
    throw std::runtime_error("BiomeComponent has not been loaded.");
}

void Biome3DComponent::set_biome(std::shared_ptr<Biome3DComponentData> component)
{
    if (_value) {
        auto& old_data = **_value;
        if (old_data.get_sections().get_array_shape() != component->get_sections().get_array_shape()) {
            throw std::invalid_argument("New biome array shape does not match old array shape.");
        }
        if (old_data.get_palette().get_version_range() != component->get_palette().get_version_range()) {
            throw std::invalid_argument("New biome version range does not match old version range.");
        }
        _value = component;
    } else {
        throw std::runtime_error("BiomeComponent has not been loaded.");
    }
}

} // namespace Amulet
