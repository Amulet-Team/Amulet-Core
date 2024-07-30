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
        writer.writeSizeAndBytes(get_platform());
        get_version().serialise(writer);
        writer.writeSizeAndBytes(namespace_);
        writer.writeSizeAndBytes(base_name);
        
    }
    Block Block::deserialise(Amulet::BinaryReader& reader){
        auto version_number = reader.readNumeric<std::uint8_t>();
        switch (version_number) {
        case 1:
        {
            std::string platform = reader.readSizeAndBytes();
            VersionNumber version = VersionNumber::deserialise(reader);
            std::string namespace_ = reader.readSizeAndBytes();
            std::string base_name = reader.readSizeAndBytes();
            // TODO: properties
            return Block(platform, version, namespace_, base_name);
        }
        default:
            throw std::invalid_argument("Unsupported version " + std::to_string(version_number));
        }
    }
}
