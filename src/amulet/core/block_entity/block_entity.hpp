#pragma once

#include <map>
#include <string>
#include <variant>

#include <amulet/io/binary_reader.hpp>
#include <amulet/io/binary_writer.hpp>

#include <amulet/nbt/tag/eq.hpp>
#include <amulet/nbt/tag/named_tag.hpp>

#include <amulet/core/dll.hpp>
#include <amulet/core/version/version.hpp>

namespace Amulet {
class BlockEntity : public PlatformVersionContainer {
private:
    std::string _namespace;
    std::string _base_name;
    std::shared_ptr<Amulet::NBT::NamedTag> _nbt;

public:
    AMULET_CORE_EXPORT const std::string& get_namespace() const;
    AMULET_CORE_EXPORT void set_namespace(const std::string& namespace_);

    AMULET_CORE_EXPORT const std::string& get_base_name() const;
    AMULET_CORE_EXPORT void set_base_name(const std::string& base_name);

    AMULET_CORE_EXPORT std::shared_ptr<Amulet::NBT::NamedTag> get_nbt() const;
    AMULET_CORE_EXPORT void set_nbt(std::shared_ptr<Amulet::NBT::NamedTag> nbt);

    AMULET_CORE_EXPORT BlockEntity(
        const PlatformType& platform,
        const VersionNumber& version,
        const std::string& namespace_,
        const std::string& base_name,
        std::shared_ptr<Amulet::NBT::NamedTag> nbt);

    AMULET_CORE_EXPORT void serialise(BinaryWriter&) const;
    AMULET_CORE_EXPORT static BlockEntity deserialise(BinaryReader&);

    AMULET_CORE_EXPORT bool operator==(const BlockEntity& other) const;
};
}
