#include <amulet/core/dll.hpp>

#include "block_entity_component.hpp"

namespace Amulet {

// BlockEntityComponentData

void BlockEntityComponentData::serialise(BinaryWriter&) const
{
    throw std::runtime_error("NotImplementedError");
}
BlockEntityComponentData BlockEntityComponentData::deserialise(BinaryReader&)
{
    throw std::runtime_error("NotImplementedError");
}

// BlockEntityComponent
AMULET_CORE_EXPORT void BlockEntityComponent::init(
    const VersionRange& version_range,
    std::uint16_t x_size,
    std::uint16_t z_size)
{
    _value = std::make_shared<BlockEntityComponentData>(version_range, x_size, z_size);
}

std::optional<std::string> BlockEntityComponent::serialise() const
{
    if (_value) {
        return Amulet::serialise(**_value);
    } else {
        return std::nullopt;
    }
}

void BlockEntityComponent::deserialise(std::optional<std::string> data)
{
    if (data) {
        _value = std::make_shared<BlockEntityComponentData>(Amulet::deserialise<BlockEntityComponentData>(*data));
    } else {
        _value = std::nullopt;
    }
}

const std::string BlockEntityComponent::ComponentID = "Amulet::BlockEntityComponent";

AMULET_CORE_EXPORT std::shared_ptr<BlockEntityComponentData> BlockEntityComponent::get_block_entity()
{
    if (_value) {
        return *_value;
    }
    throw std::runtime_error("BlockEntityComponent has not been loaded.");
}

AMULET_CORE_EXPORT void BlockEntityComponent::set_block_entity(std::shared_ptr<BlockEntityComponentData> component)
{
    if (_value) {
        auto& old_data = **_value;
        if (old_data.get_x_size() != component->get_x_size() || old_data.get_z_size() != component->get_z_size()) {
            throw std::invalid_argument("New BlockEntityComponent shape does not match old shape.");
        }
        if (old_data.get_version_range() != component->get_version_range()) {
            throw std::invalid_argument("New BlockEntityComponent version range does not match old version range.");
        }
        _value = component;
    } else {
        throw std::runtime_error("BlockEntityComponent has not been loaded.");
    }
}

} // namespace Amulet
