#include <amulet/core/dll.hpp>

#include "block_component.hpp"

namespace Amulet {

// BlockStorage
void BlockStorage::serialise(BinaryWriter& writer) const
{
    writer.write_numeric<std::uint8_t>(1);
    get_palette().serialise(writer);
    get_sections().serialise(writer);
}

BlockStorage BlockStorage::deserialise(BinaryReader& reader)
{
    auto version = reader.read_numeric<std::uint8_t>();
    switch (version) {
    case 1: {
        auto palette = std::make_shared<BlockPalette>(Amulet::deserialise<BlockPalette>(reader));
        auto sections = std::make_shared<SectionArrayMap>(Amulet::deserialise<SectionArrayMap>(reader));
        return { palette, sections };
    }
    default:
        throw std::invalid_argument("Unsupported BlockStorage version " + std::to_string(version));
    }
}

// BlockComponent
std::optional<std::string> BlockComponent::serialise() const
{
    if (_value) {
        return Amulet::serialise(**_value);
    } else {
        return std::nullopt;
    }
}

void BlockComponent::deserialise(std::optional<std::string> data)
{
    if (data) {
        _value = std::make_shared<BlockStorage>(Amulet::deserialise<BlockStorage>(*data));
    } else {
        _value = std::nullopt;
    }
}

const std::string BlockComponent::ComponentID = "Amulet::BlockComponent";

std::shared_ptr<BlockStorage> BlockComponent::get_block_storage()
{
    if (_value) {
        return *_value;
    }
    throw std::runtime_error("BlockComponent has not been loaded.");
}

void BlockComponent::set_block_storage(std::shared_ptr<BlockStorage> component)
{
    if (_value) {
        auto& old_data = **_value;
        if (old_data.get_sections().get_array_shape() != component->get_sections().get_array_shape()) {
            throw std::invalid_argument("New block array shape does not match old array shape.");
        }
        if (old_data.get_palette().get_version_range() != component->get_palette().get_version_range()) {
            throw std::invalid_argument("New block version range does not match old version range.");
        }
        _value = component;
    } else {
        throw std::runtime_error("BlockComponent has not been loaded.");
    }
}

} // namespace Amulet
