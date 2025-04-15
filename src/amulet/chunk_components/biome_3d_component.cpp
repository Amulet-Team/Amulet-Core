#include <amulet/dll.hpp>

#include "biome_3d_component.hpp"

namespace Amulet {

// Biome3DComponentData
Biome3DComponentData::Biome3DComponentData(
    const VersionRange& version_range,
    const SectionShape& array_shape,
    const Biome& default_biome)
    : _palette(std::make_shared<BiomePalette>(version_range))
    , _sections(std::make_shared<SectionArrayMap>(array_shape, static_cast<std::uint32_t>(0)))
{
    _palette->biome_to_index(default_biome);
}

std::shared_ptr<BiomePalette> Biome3DComponentData::get_palette()
{
    return _palette;
}

std::shared_ptr<SectionArrayMap> Biome3DComponentData::get_sections()
{
    return _sections;
}

// Biome3DComponent
void Biome3DComponent::init(
    const VersionRange& version_range,
    const SectionShape& array_shape,
    const Biome& default_biome)
{
    _value = std::make_shared<Biome3DComponentData>(version_range, array_shape, default_biome);
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
        if ((*_value)->get_sections()->get_array_shape() != component->get_sections()->get_array_shape()) {
            throw std::invalid_argument("New biome array shape does not match old array shape.");
        }
        if ((*_value)->get_palette()->get_version_range() != component->get_palette()->get_version_range()) {
            throw std::invalid_argument("New biome version range does not match old version range.");
        }
        _value = component;
    } else {
        throw std::runtime_error("BiomeComponent has not been loaded.");
    }
}

} // namespace Amulet
