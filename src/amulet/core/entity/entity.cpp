#include <amulet/nbt/nbt_encoding/binary.hpp>

#include <amulet/core/dll.hpp>
#include <amulet/core/version/version.hpp>

#include "entity.hpp"

namespace Amulet {

void Entity::serialise(BinaryWriter& writer) const
{
    writer.write_numeric<std::uint8_t>(1);
    writer.write_size_and_bytes(get_platform());
    get_version().serialise(writer);
    writer.write_size_and_bytes(_namespace);
    writer.write_size_and_bytes(_base_name);
    writer.write_numeric<double>(_x);
    writer.write_numeric<double>(_y);
    writer.write_numeric<double>(_z);
    Amulet::NBT::encode_nbt(writer, *_nbt);
}

Entity Entity::deserialise(BinaryReader& reader)
{
    auto version_number = reader.read_numeric<std::uint8_t>();
    switch (version_number) {
    case 1: {
        std::string platform { reader.read_size_and_bytes() };
        VersionNumber version = VersionNumber::deserialise(reader);
        std::string namespace_ { reader.read_size_and_bytes() };
        std::string base_name { reader.read_size_and_bytes() };
        double x = reader.read_numeric<double>();
        double y = reader.read_numeric<double>();
        double z = reader.read_numeric<double>();
        auto named_tag = std::make_shared<Amulet::NBT::NamedTag>(Amulet::NBT::decode_nbt(reader));
        return Entity {
            std::move(platform),
            std::move(version),
            std::move(namespace_),
            std::move(base_name),
            x,
            y,
            z,
            std::move(named_tag)
        };
    }
    default:
        throw std::invalid_argument("Unsupported BlockEntity version " + std::to_string(version_number));
    }
}

bool Entity::operator==(const Entity& other) const
{
    return (
        PlatformVersionContainer::operator==(other)
        && _namespace == other._namespace
        && _base_name == other._base_name
        && _x == other._x
        && _y == other._y
        && _z == other._z
        && Amulet::NBT::NBTTag_eq(*_nbt, *other._nbt));
}

} // namespace Amulet
