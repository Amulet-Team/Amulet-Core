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
            
            auto operator<=>(const Block&) const = default;
    };

    class BlockStack {
        private:
            std::vector<Block> blocks;
        public:
            const std::vector<Block>& get_blocks() const { return blocks; }

            BlockStack(std::initializer_list<Block> blocks) : blocks(blocks) {}
            BlockStack(const std::vector<Block>& blocks) : blocks(blocks) {}

            auto operator<=>(const BlockStack&) const = default;

            std::vector<Block>::const_iterator begin() const { return blocks.begin(); }
            std::vector<Block>::const_iterator end() const { return blocks.end(); }
            std::vector<Block>::const_reverse_iterator rbegin() const { return blocks.rbegin(); }
            std::vector<Block>::const_reverse_iterator rend() const { return blocks.rend(); }
            size_t size() const { return blocks.size(); }
            const Block& operator[](size_t index) const { return blocks[index]; };
    };
}
