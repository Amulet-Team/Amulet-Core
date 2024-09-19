#pragma once

#include <map>
#include <variant>
#include <string>

#include <amulet/io/binary_reader.hpp>
#include <amulet/io/binary_writer.hpp>
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

    typedef std::map<std::string, PropertyValueType> BlockProperites;

    class Block: public PlatformVersionContainer {
        private:
            std::string namespace_;
            std::string base_name;
            BlockProperites properties;
        public:
            const std::string& get_namespace() const { return namespace_; }
            const std::string& get_base_name() const { return base_name; }
            const BlockProperites& get_properties() const {
                return properties;
            }

            template <typename versionT>
            Block(
                const PlatformType& platform,
                const versionT& version,
                const std::string& namespace_,
                const std::string& base_name
            ) :
                PlatformVersionContainer(platform, version),
                namespace_(namespace_),
                base_name(base_name),
                properties() {}

            template <
                typename versionT,
                typename propertiesT
            >
            Block(
                const PlatformType& platform,
                const versionT& version,
                const std::string& namespace_,
                const std::string& base_name,
                const propertiesT& properties
            ):
                PlatformVersionContainer(platform, version),
                namespace_(namespace_),
                base_name(base_name),
                properties(properties) {}

            void serialise(BinaryWriter&) const;
            static std::shared_ptr<Block> deserialise(BinaryReader&);
            
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
            std::vector<std::shared_ptr<Block>> _blocks;
        public:
            const std::vector<std::shared_ptr<Block>>& get_blocks() const { return _blocks; }

            template <typename T>
            BlockStack(const T& blocks) : _blocks(blocks) {
                if (_blocks.empty()) {
                    throw std::invalid_argument("A BlockStack must contain at least one block");
                }
            }

            void serialise(BinaryWriter&) const;
            static std::shared_ptr<BlockStack> deserialise(BinaryReader&);

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

            size_t size() const { return _blocks.size(); }
            std::shared_ptr<Block> operator[](size_t index) const { return _blocks[index]; };
    };
}
