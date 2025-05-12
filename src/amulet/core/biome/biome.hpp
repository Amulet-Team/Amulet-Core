#pragma once

#include <string>

#include <amulet/io/binary_reader.hpp>
#include <amulet/io/binary_writer.hpp>

#include <amulet/core/dll.hpp>
#include <amulet/core/version/version.hpp>

namespace Amulet {
class Biome : public PlatformVersionContainer {
private:
    std::string _namespace;
    std::string _base_name;

public:
    const std::string& get_namespace() const { return _namespace; }
    const std::string& get_base_name() const { return _base_name; }

    template <typename PlatformT, typename VersionT, typename NamespaceT, typename BaseNameT>
    Biome(
        PlatformT&& platform,
        VersionT&& version,
        NamespaceT&& namespace_,
        BaseNameT&& base_name)
        : PlatformVersionContainer(std::forward<PlatformT>(platform), std::forward<VersionT>(version))
        , _namespace(std::forward<NamespaceT>(namespace_))
        , _base_name(std::forward<BaseNameT>(base_name))
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
        cmp = _namespace <=> other._namespace;
        if (cmp != 0) {
            return cmp;
        }
        return _base_name <=> other._base_name;
    }
    bool operator==(const Biome& other) const
    {
        return (*this <=> other) == 0;
    }
};
}
