#pragma once

#include <map>
#include <variant>
#include <string>

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
                const PlatformType& platform,
                std::shared_ptr<VersionNumber> version,
                const std::string& namespace_,
                const std::string& base_name,
                const std::map<std::string, PropertyValueType>& properties = std::map<std::string, PropertyValueType>()
            ):
                PlatformVersionContainer(platform, version),
                namespace_(namespace_),
                base_name(base_name),
                properties(properties) {}

            void serialise(Amulet::BinaryWriter&) const;
            static std::shared_ptr<Block> deserialise(Amulet::BinaryReader&);
            
            auto operator<=>(const Block& other) const {
                auto cmp = PlatformVersionContainer::operator<=>(other);
                if (cmp != 0) { return cmp; }
                cmp = namespace_ <=> other.namespace_;
                if (cmp != 0) { return cmp; }
                cmp = base_name <=> other.base_name;
                if (cmp != 0) { return cmp; }
                return properties <=> other.properties;
            }
            bool operator==(const Block& other) const {
                return (*this <=> other) == 0;
            };

            std::string java_blockstate() const;
            std::string bedrock_blockstate() const;
            static std::shared_ptr<Block> from_java_blockstate(const PlatformType&, std::shared_ptr<VersionNumber>, const std::string&);
            static std::shared_ptr<Block> from_bedrock_blockstate(const PlatformType&, std::shared_ptr<VersionNumber>, const std::string&);
    };

    class BlockStack {
        private:
            std::vector<std::shared_ptr<Block>> blocks;
        public:
            const std::vector<std::shared_ptr<Block>>& get_blocks() const { return blocks; }

            BlockStack(std::initializer_list<std::shared_ptr<Block>> blocks) : blocks(blocks) {}
            BlockStack(const std::vector<std::shared_ptr<Block>>& blocks) : blocks(blocks) {}

            void serialise(Amulet::BinaryWriter&) const;
            static std::shared_ptr<BlockStack> deserialise(Amulet::BinaryReader&);

            auto operator<=>(const BlockStack& other) const {
                auto cmp = size() <=> other.size();
                if (cmp != 0) { return cmp; }
                for (size_t i = 0; i < size(); i++) {
                    cmp = *(*this)[i] <=> *other[i];
                    if (cmp != 0) { return cmp; }
                }
                return std::strong_ordering::equal;
            }
            bool operator==(const BlockStack& other) const {
                return (*this <=> other) == 0;
            };

            size_t size() const { return blocks.size(); }
            std::shared_ptr<Block> operator[](size_t index) const { return blocks[index]; };
    };
}
