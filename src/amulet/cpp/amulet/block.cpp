#include <map>
#include <variant>
#include <type_traits>

#include <amulet/block.hpp>
#include <amulet_nbt/nbt_encoding/binary.hpp>

namespace Amulet {
    Block::Block(
        const PlatformType& platform,
        const VersionNumber& version,
        const std::string& namespace_,
        const std::string& base_name,
        const std::map<std::string, PropertyValueType>& properties
    ): 
        PlatformVersionContainer(platform, version), 
        namespace_(namespace_), 
        base_name(base_name), 
        properties(properties) {}

    void Block::serialise(Amulet::BinaryWriter& writer) const {
        writer.writeNumeric<std::uint8_t>(1);
        writer.writeSizeAndBytes(get_platform());
        get_version().serialise(writer);
        writer.writeSizeAndBytes(namespace_);
        writer.writeSizeAndBytes(base_name);
        
        writer.writeNumeric<std::uint64_t>(properties.size());
        for (auto const& [key, val] : properties) {
            writer.writeSizeAndBytes(key);
            std::visit([&writer](auto&& tag) {
                AmuletNBT::write_nbt(writer, "", tag);
            }, val);
        }
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
            std::uint64_t property_count;
            std::map<std::string, PropertyValueType> properties;
            reader.readNumericInto<std::uint64_t>(property_count);
            for (std::uint64_t i = 0; i < property_count; i++) {
                std::string name = reader.readSizeAndBytes();
                AmuletNBT::NamedTag named_tag = AmuletNBT::read_nbt(reader);
                properties[name] = std::visit([](auto&& tag) -> PropertyValueType {
                    using T = std::decay_t<decltype(tag)>;
                    if constexpr (
                        std::is_same_v<T, AmuletNBT::ByteTag> ||
                        std::is_same_v<T, AmuletNBT::ShortTag> ||
                        std::is_same_v<T, AmuletNBT::IntTag> ||
                        std::is_same_v<T, AmuletNBT::LongTag> ||
                        std::is_same_v<T, AmuletNBT::StringTag>
                    ) {
                        return tag;
                    }
                    else {
                        throw std::invalid_argument("Property tag must be Byte, Short, Int, Long or String");
                    }
                }, named_tag.tag_node);
            }
            return Block(platform, version, namespace_, base_name, properties);
        }
        default:
            throw std::invalid_argument("Unsupported version " + std::to_string(version_number));
        }
    }
}
