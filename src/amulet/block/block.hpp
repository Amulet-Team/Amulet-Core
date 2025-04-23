#pragma once

#include <map>
#include <string>
#include <variant>

#include <amulet/core/dll.hpp>
#include <amulet/io/binary_reader.hpp>
#include <amulet/io/binary_writer.hpp>
#include <amulet/version/version.hpp>
#include <amulet/nbt/tag/int.hpp>
#include <amulet/nbt/tag/string.hpp>

namespace Amulet {
typedef std::variant<
    Amulet::NBT::ByteTag,
    Amulet::NBT::ShortTag,
    Amulet::NBT::IntTag,
    Amulet::NBT::LongTag,
    Amulet::NBT::StringTag>
    PropertyValueType;

typedef std::map<std::string, PropertyValueType> BlockProperites;

class Block : public PlatformVersionContainer {
private:
    std::string namespace_;
    std::string base_name;
    BlockProperites properties;

public:
    const std::string& get_namespace() const { return namespace_; }
    const std::string& get_base_name() const { return base_name; }
    const BlockProperites& get_properties() const
    {
        return properties;
    }

    Block(
        const PlatformType& platform,
        const VersionNumber& version,
        const std::string& namespace_,
        const std::string& base_name)
        : PlatformVersionContainer(platform, version)
        , namespace_(namespace_)
        , base_name(base_name)
        , properties()
    {
    }

    template <typename propertiesT>
    Block(
        const PlatformType& platform,
        const VersionNumber& version,
        const std::string& namespace_,
        const std::string& base_name,
        const propertiesT& properties)
        : PlatformVersionContainer(platform, version)
        , namespace_(namespace_)
        , base_name(base_name)
        , properties(properties)
    {
    }

    AMULET_CORE_EXPORT void serialise(BinaryWriter&) const;
    AMULET_CORE_EXPORT static Block deserialise(BinaryReader&);

    auto operator<=>(const Block& other) const
    {
        auto cmp = PlatformVersionContainer::operator<=>(other);
        if (cmp != 0) {
            return cmp;
        }
        cmp = namespace_ <=> other.namespace_;
        if (cmp != 0) {
            return cmp;
        }
        cmp = base_name <=> other.base_name;
        if (cmp != 0) {
            return cmp;
        }
        return properties <=> other.properties;
    }
    bool operator==(const Block& other) const
    {
        return (*this <=> other) == 0;
    }

    AMULET_CORE_EXPORT std::string java_blockstate() const;
    AMULET_CORE_EXPORT std::string bedrock_blockstate() const;
    AMULET_CORE_EXPORT static Block from_java_blockstate(const PlatformType&, const VersionNumber&, const std::string&);
    AMULET_CORE_EXPORT static Block from_bedrock_blockstate(const PlatformType&, const VersionNumber&, const std::string&);
};

class BlockStack {
private:
    std::vector<Block> _blocks;

public:
    const std::vector<Block>& get_blocks() const { return _blocks; }

    template <typename... Args>
        requires std::is_constructible_v<std::vector<Block>, Args...>
    BlockStack(Args&&... args)
        : _blocks(std::forward<Args>(args)...)
    {
        if (_blocks.empty()) {
            throw std::invalid_argument("A BlockStack must contain at least one block");
        }
    }

    BlockStack(std::initializer_list<Block> blocks)
        : _blocks(blocks)
    {
        if (_blocks.empty()) {
            throw std::invalid_argument("A BlockStack must contain at least one block");
        }
    }

    AMULET_CORE_EXPORT void serialise(BinaryWriter&) const;
    AMULET_CORE_EXPORT static BlockStack deserialise(BinaryReader&);

    auto operator<=>(const BlockStack& other) const
    {
        auto cmp = size() <=> other.size();
        if (cmp != 0) {
            return cmp;
        }
        for (size_t i = 0; i < size(); i++) {
            cmp = (*this)[i] <=> other[i];
            if (cmp != 0) {
                return cmp;
            }
        }
        return std::strong_ordering::equal;
    }
    bool operator==(const BlockStack& other) const
    {
        return (*this <=> other) == 0;
    }

    size_t size() const { return _blocks.size(); }
    const Block& operator[](size_t index) const { return _blocks[index]; }
};
}
