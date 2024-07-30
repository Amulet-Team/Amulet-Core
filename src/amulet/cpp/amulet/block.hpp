#include <map>
#include <variant>

#include <amulet/version.hpp>
#include <amulet_nbt/tag/int.hpp>
#include <amulet_nbt/tag/string.hpp>


namespace Amulet {
    typedef std::variant<
        AmuletNBT::ByteTag,
        AmuletNBT::ShortTag,
        AmuletNBT::IntTag,
        AmuletNBT::LongTag,
        AmuletNBT::StringTag
    > PropertyValueType;

    class Block: public PlatformVersionContainer {
        private:
            std::string namespace_;
            std::string base_name;
            std::map<std::string, PropertyValueType> properties;
        public:
            const std::string& get_namespace() const { return namespace_; }
            const std::string& get_base_name() const { return base_name; }
            const std::map<std::string, PropertyValueType>& get_properties() const {
                return properties;
            }

            Block(
                const PlatformType&,
                const VersionNumber&,
                const std::string& namespace_,
                const std::string& base_name,
                const std::map<std::string, PropertyValueType>&
            );

            void serialise(Amulet::BinaryWriter&) const;
            static Block deserialise(Amulet::BinaryReader&);
            
    };
}
