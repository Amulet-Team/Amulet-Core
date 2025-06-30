#include <amulet/core/dll.hpp>

#include "block_entity_component.hpp"

namespace Amulet {

// BlockEntityComponentData

void BlockEntityComponentData::serialise(BinaryWriter& writer) const
{
    writer.write_numeric<std::uint8_t>(1);
    get_version_range().serialise(writer);
    writer.write_numeric<std::uint16_t>(get_x_size());
    writer.write_numeric<std::uint16_t>(get_z_size());

    writer.write_numeric<std::uint64_t>(get_block_entities().size());
    for (const auto& [coord, block_entity] : get_block_entities()) {
        writer.write_numeric<std::uint16_t>(std::get<0>(coord));
        writer.write_numeric<std::int64_t>(std::get<1>(coord));
        writer.write_numeric<std::uint16_t>(std::get<2>(coord));
        block_entity->serialise(writer);
    }
}
BlockEntityComponentData BlockEntityComponentData::deserialise(BinaryReader& reader)
{
    auto version_number = reader.read_numeric<std::uint8_t>();
    switch (version_number) {
    case 1: {
        auto version_range = VersionRange::deserialise(reader);
        auto x_size = reader.read_numeric<std::uint16_t>();
        auto z_size = reader.read_numeric<std::uint16_t>();
        BlockEntityComponentData block_entities {
            std::move(version_range),
            x_size,
            z_size
        };
        auto block_entity_count = reader.read_numeric<std::uint64_t>();
        for (std::uint16_t i = 0; i < block_entity_count; i++) {
            auto dx = reader.read_numeric<std::uint16_t>();
            auto y = reader.read_numeric<std::int64_t>();
            auto dz = reader.read_numeric<std::uint16_t>();
            auto block_entity = std::make_shared<BlockEntity>(BlockEntity::deserialise(reader));
            block_entities.set({ dx, y, dz }, std::move(block_entity));
        }
        return block_entities;
    }
    default:
        throw std::invalid_argument("Unsupported BlockEntityComponentData version " + std::to_string(version_number));
    }
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
