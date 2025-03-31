#pragma once

#include <map>
#include <string>
#include <variant>

#include <amulet/dll.hpp>
#include <amulet/io/binary_reader.hpp>
#include <amulet/io/binary_writer.hpp>
#include <amulet/version.hpp>
#include <amulet_nbt/tag/eq.hpp>
#include <amulet_nbt/tag/named_tag.hpp>

namespace Amulet {
class BlockEntity : public PlatformVersionContainer {
private:
    std::string _namespace;
    std::string _base_name;
    std::shared_ptr<AmuletNBT::NamedTag> _nbt;

public:
    AMULET_CORE_EXPORT const std::string& get_namespace() const;
    AMULET_CORE_EXPORT void set_namespace(const std::string& namespace_);

    AMULET_CORE_EXPORT const std::string& get_base_name() const;
    AMULET_CORE_EXPORT void set_base_name(const std::string& base_name);

    AMULET_CORE_EXPORT std::shared_ptr<AmuletNBT::NamedTag> get_nbt() const;
    AMULET_CORE_EXPORT void set_nbt(std::shared_ptr<AmuletNBT::NamedTag> nbt);

    AMULET_CORE_EXPORT BlockEntity(
        const PlatformType& platform,
        const VersionNumber& version,
        const std::string& namespace_,
        const std::string& base_name,
        std::shared_ptr<AmuletNBT::NamedTag> nbt);

    AMULET_CORE_EXPORT void serialise(BinaryWriter&) const;
    AMULET_CORE_EXPORT static BlockEntity deserialise(BinaryReader&);

    AMULET_CORE_EXPORT bool operator==(const BlockEntity& other) const;
};
}
