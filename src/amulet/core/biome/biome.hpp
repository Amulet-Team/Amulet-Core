#pragma once

#include <string>

#include <amulet/io/binary_reader.hpp>
#include <amulet/io/binary_writer.hpp>

#include <amulet/core/dll.hpp>
#include <amulet/core/version/version.hpp>

namespace Amulet {
class Biome : public PlatformVersionContainer {
private:
    std::string namespace_;
    std::string base_name;

public:
    const std::string& get_namespace() const { return namespace_; }
    const std::string& get_base_name() const { return base_name; }

    template <typename PlatformT, typename VersionT, typename NamespaceT, typename BaseNameT>
    Biome(
        PlatformT&& platform,
        VersionT&& version,
        NamespaceT&& namespace_,
        BaseNameT&& base_name)
        : PlatformVersionContainer(std::forward<PlatformT>(platform), std::forward<VersionT>(version))
        , namespace_(std::forward<NamespaceT>(namespace_))
        , base_name(std::forward<BaseNameT>(base_name))
    {
    }

    AMULET_CORE_EXPORT void serialise(BinaryWriter&) const;
    AMULET_CORE_EXPORT static Biome deserialise(BinaryReader&);

    auto operator<=>(const Biome& other) const
    {
        auto cmp = PlatformVersionContainer::operator<=>(other);
        if (cmp != 0) {
            return cmp;
        }
        cmp = namespace_ <=> other.namespace_;
        if (cmp != 0) {
            return cmp;
        }
        return base_name <=> other.base_name;
    }
    bool operator==(const Biome& other) const
    {
        return (*this <=> other) == 0;
    }
};
}
