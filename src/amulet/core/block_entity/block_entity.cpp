#include <amulet/nbt/nbt_encoding/binary.hpp>

#include <amulet/core/dll.hpp>

#include "block_entity.hpp"

namespace Amulet {

void BlockEntity::serialise(BinaryWriter& writer) const
{
    writer.write_numeric<std::uint8_t>(1);
    writer.write_size_and_bytes(get_platform());
    get_version().serialise(writer);
    writer.write_size_and_bytes(_namespace);
    writer.write_size_and_bytes(_base_name);
    Amulet::NBT::encode_nbt(writer, *_nbt);
}

BlockEntity BlockEntity::deserialise(BinaryReader& reader)
{
    auto version_number = reader.read_numeric<std::uint8_t>();
    switch (version_number) {
    case 1: {
        std::string platform { reader.read_size_and_bytes() };
        VersionNumber version = VersionNumber::deserialise(reader);
        std::string namespace_ { reader.read_size_and_bytes() };
        std::string base_name { reader.read_size_and_bytes() };
        auto named_tag = std::make_shared<Amulet::NBT::NamedTag>(Amulet::NBT::decode_nbt(reader));
        return BlockEntity {
            std::move(platform),
            std::move(version),
            std::move(namespace_),
            std::move(base_name),
            std::move(named_tag)
        };
    }
    default:
        throw std::invalid_argument("Unsupported BlockEntity version " + std::to_string(version_number));
    }
}

bool BlockEntity::operator==(const BlockEntity& other) const
{
    return (
        PlatformVersionContainer::operator==(other)
        && _namespace == other._namespace
        && _base_name == other._base_name
        && Amulet::NBT::NBTTag_eq(*_nbt, *other._nbt));
}

}
