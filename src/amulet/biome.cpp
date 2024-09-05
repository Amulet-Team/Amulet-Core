#include <map>
#include <variant>
#include <type_traits>
#include <string>
#include <functional>
#include <stdexcept>

#include <amulet/biome.hpp>
#include <amulet_nbt/nbt_encoding/binary.hpp>
#include <amulet_nbt/nbt_encoding/string.hpp>

namespace Amulet {
    void Biome::serialise(BinaryWriter& writer) const {
        writer.writeNumeric<std::uint8_t>(1);
        writer.writeSizeAndBytes(get_platform());
        get_version()->serialise(writer);
        writer.writeSizeAndBytes(namespace_);
        writer.writeSizeAndBytes(base_name);
    }
    std::shared_ptr<Biome> Biome::deserialise(BinaryReader& reader){
        auto version_number = reader.readNumeric<std::uint8_t>();
        switch (version_number) {
        case 1:
        {
            std::string platform = reader.readSizeAndBytes();
            std::shared_ptr<VersionNumber> version = VersionNumber::deserialise(reader);
            std::string namespace_ = reader.readSizeAndBytes();
            std::string base_name = reader.readSizeAndBytes();
            return std::make_shared<Biome>(platform, version, namespace_, base_name);
        }
        default:
            throw std::invalid_argument("Unsupported version " + std::to_string(version_number));
        }
    }

}
