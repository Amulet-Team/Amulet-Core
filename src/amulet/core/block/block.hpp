#pragma once

#include <map>
#include <string>
#include <variant>

#include <amulet/io/binary_reader.hpp>
#include <amulet/io/binary_writer.hpp>

#include <amulet/nbt/tag/int.hpp>
#include <amulet/nbt/tag/string.hpp>

#include <amulet/core/dll.hpp>
#include <amulet/core/version/version.hpp>

namespace Amulet {

class Block : public PlatformVersionContainer {
public:
    using PropertyValue = std::variant<
        Amulet::NBT::ByteTag,
        Amulet::NBT::ShortTag,
        Amulet::NBT::IntTag,
        Amulet::NBT::LongTag,
        Amulet::NBT::StringTag>;

    using PropertyMap = std::map<std::string, PropertyValue>;

private:
    std::string _namespace;
    std::string _base_name;
    PropertyMap _properties;

public:
    const std::string& get_namespace() const { return _namespace; }
    const std::string& get_base_name() const { return _base_name; }
    const PropertyMap& get_properties() const { return _properties; }

    template <
        typename PlatformT,
        typename VersionT,
        typename NamespaceT,
        typename BaseNameT>
    Block(
        PlatformT&& platform,
        VersionT&& version,
        NamespaceT&& namespace_,
        BaseNameT&& base_name)
        : PlatformVersionContainer(std::forward<PlatformT>(platform), std::forward<VersionT>(version))
        , _namespace(std::forward<NamespaceT>(namespace_))
        , _base_name(std::forward<BaseNameT>(base_name))
        , _properties()
    {
    }

    template <
        typename PlatformT,
        typename VersionT,
        typename NamespaceT,
        typename BaseNameT,
        typename PropertiesT>
    Block(
        PlatformT&& platform,
        VersionT&& version,
        NamespaceT&& namespace_,
        BaseNameT&& base_name,
        PropertiesT&& properties)
        : PlatformVersionContainer(std::forward<PlatformT>(platform), std::forward<VersionT>(version))
        , _namespace(std::forward<NamespaceT>(namespace_))
        , _base_name(std::forward<BaseNameT>(base_name))
        , _properties(std::forward<PropertiesT>(properties))
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
        cmp = _namespace <=> other._namespace;
        if (cmp != 0) {
            return cmp;
        }
        cmp = _base_name <=> other._base_name;
        if (cmp != 0) {
            return cmp;
        }
        return _properties <=> other._properties;
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
            cmp = at(i) <=> other.at(i);
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
    const Block& at(size_t index) const { return _blocks.at(index); }
};

} // namespace Amulet
