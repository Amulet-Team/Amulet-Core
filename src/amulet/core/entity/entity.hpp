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

class Entity : public PlatformVersionContainer {
private:
    std::string _namespace;
    std::string _base_name;
    std::shared_ptr<Amulet::NBT::NamedTag> _nbt;
    double _x;
    double _y;
    double _z;

public:
    const std::string& get_namespace() const { return _namespace; }

    template <typename NamespaceT>
    void set_namespace(NamespaceT&& namespace_) { _namespace = std::forward<NamespaceT>(namespace_); }

    const std::string& get_base_name() const { return _base_name; }

    template <typename BaseNameT>
    void set_base_name(BaseNameT&& base_name) { _base_name = std::forward<BaseNameT>(base_name); }

    std::shared_ptr<Amulet::NBT::NamedTag> get_nbt() const { return _nbt; }

    template <typename NBTT>
    void set_nbt(NBTT&& nbt)
    {
        if constexpr (std::is_same_v<std::shared_ptr<Amulet::NBT::NamedTag>, std::decay_t<NBTT>>) {
            _nbt = std::forward<NBTT>(nbt);
        } else {
            _nbt = std::make_shared<Amulet::NBT::NamedTag>(std::forward<NBTT>(nbt));
        }
    }

    double get_x() const { return _x; }

    double get_y() const { return _y; }

    double get_z() const { return _z; }

    void set_x(double x) { _x = x; }

    void set_y(double y) { _y = y; }

    void set_z(double z) { _z = z; }

    template <
        typename PlatformT,
        typename VersionNumberT,
        typename NamespaceT,
        typename BaseNameT,
        typename NBTT>
    Entity(
        PlatformT&& platform,
        VersionNumberT&& version,
        NamespaceT&& namespace_,
        BaseNameT&& base_name,
        double x,
        double y,
        double z,
        NBTT&& nbt)
        : PlatformVersionContainer(std::forward<PlatformT>(platform), std::forward<VersionNumberT>(version))
        , _namespace(std::forward<NamespaceT>(namespace_))
        , _base_name(std::forward<BaseNameT>(base_name))
        , _nbt(
              [&nbt]() {
                  if constexpr (std::is_same_v<std::shared_ptr<Amulet::NBT::NamedTag>, NBTT>) {
                      return std::forward<NBTT>(nbt);
                  } else {
                      return std::make_shared<Amulet::NBT::NamedTag>(std::forward<NBTT>(nbt));
                  }
              }())
        , _x(x)
        , _y(y)
        , _z(z)
    {
    }

    AMULET_CORE_EXPORT void serialise(BinaryWriter&) const;
    AMULET_CORE_EXPORT static Entity deserialise(BinaryReader&);

    AMULET_CORE_EXPORT bool operator==(const Entity& other) const;
};

} // namespace Amulet
