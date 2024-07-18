#include <map>

#include <amulet/block.hpp>

namespace Amulet {
    Block::Block(
        const PlatformType& platform,
        const VersionNumber& version,
        const std::string& namespace_,
        const std::string& base_name,
        const std::map<std::string, > properties
    ) : PlatformVersionContainer(platform, version), namespace_(namespace_), base_name(base_name) {}

    void Block::serialise(Amulet::BinaryWriter& writer) const {
        writer.writeNumeric<std::uint8_t>(1);
        writer.writeString(platform);
        version.serialise(writer);
        writer.writeString(namespace_);
        writer.writeString(base_name);
        // TODO: properties
    }
    Block Block::deserialise(Amulet::BinaryReader& reader){
        auto version_number = reader.readNumeric<std::uint8_t>();
        switch (version_number) {
        case 1:
        {
            std::string platform = reader.readString();
            VersionNumber version = VersionNumber::deserialise(reader);
            std::string namespace_ = reader.readString();
            std::string base_name = reader.readString();
            // TODO: properties
            return Block(platform, version, namespace_, base_name);
        }
        default:
            throw std::invalid_argument("Unsupported version " + std::to_string(version_number));
        }
    }
}
