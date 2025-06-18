#include <amulet/core/dll.hpp>

#include "biome_3d_component.hpp"

namespace Amulet {

// Biome3DComponent

void Biome3DComponentData::serialise(BinaryWriter& writer) const
{
    writer.write_numeric<std::uint8_t>(1);
    _palette->serialise(writer);
    _sections->serialise(writer);
}
Biome3DComponentData Biome3DComponentData::deserialise(BinaryReader& reader)
{
    auto version_number = reader.read_numeric<std::uint8_t>();
    switch (version_number) {
    case 1: {
        auto palette = std::make_shared<BiomePalette>(BiomePalette::deserialise(reader));
        auto sections = std::make_shared<SectionArrayMap>(SectionArrayMap::deserialise(reader));
        return Biome3DComponentData { std::move(palette), std::move(sections) };
    }
    default:
        throw std::invalid_argument("Unsupported Biome3DComponentData version " + std::to_string(version_number));
    }
}

std::optional<std::string> Biome3DComponent::serialise() const
{
    if (_value) {
        return Amulet::serialise(**_value);
    } else {
        return std::nullopt;
    }
}
// Deserialise the component
void Biome3DComponent::deserialise(std::optional<std::string> data)
{
    if (data) {
        _value = std::make_shared<Biome3DComponentData>(Amulet::deserialise<Biome3DComponentData>(*data));
    } else {
        _value = std::nullopt;
    }
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
