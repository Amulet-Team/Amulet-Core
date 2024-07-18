#include <map>
#include <variant>

#include <amulet/version.hpp>
#include <amulet_nbt/tag/nbt.hpp>


namespace Amulet {
    typedef std::variant<
        AmuletNBT::ByteTag,
        AmuletNBT::ShortTag,
        AmuletNBT::IntTag,
        AmuletNBT::LongTag,
        AmuletNBT::StringTag,
    > PropertyValueType;

    class Block: public PlatformVersionContainer {
        public:
            const std::string namespace_;
            const std::string base_name;
            const std::map<std::string, PropertyValueType> properties

            Block(
                const PlatformType&,
                const VersionNumber&,
                const std::string&,
                const std::string&
            );
            void serialise(Amulet::BinaryWriter&) const;
            static Block deserialise(Amulet::BinaryReader&);
    };
}
