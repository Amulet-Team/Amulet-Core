#include <functional>
#include <map>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <variant>

#include <amulet/core/dll.hpp>
#include <amulet/nbt/nbt_encoding/binary.hpp>
#include <amulet/nbt/nbt_encoding/string.hpp>

#include "biome.hpp"

namespace Amulet {

void Biome::serialise(BinaryWriter& writer) const
{
    writer.write_numeric<std::uint8_t>(1);
    writer.write_size_and_bytes(get_platform());
    get_version().serialise(writer);
    writer.write_size_and_bytes(_namespace);
    writer.write_size_and_bytes(_base_name);
}

Biome Biome::deserialise(BinaryReader& reader)
{
    auto version_number = reader.read_numeric<std::uint8_t>();
    switch (version_number) {
    case 1: {
        std::string platform { reader.read_size_and_bytes() };
        VersionNumber version = VersionNumber::deserialise(reader);
        std::string namespace_ { reader.read_size_and_bytes() };
        std::string base_name { reader.read_size_and_bytes() };
        return { platform, version, namespace_, base_name };
    }
    default:
        throw std::invalid_argument("Unsupported version " + std::to_string(version_number));
    }
}

}
