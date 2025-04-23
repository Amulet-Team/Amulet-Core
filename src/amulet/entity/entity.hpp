#pragma once

#include <map>
#include <string>
#include <variant>

#include <amulet/core/dll.hpp>
#include <amulet/io/binary_reader.hpp>
#include <amulet/io/binary_writer.hpp>
#include <amulet/version/version.hpp>
#include <amulet/nbt/tag/eq.hpp>
#include <amulet/nbt/tag/named_tag.hpp>

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
    AMULET_CORE_EXPORT const std::string& get_namespace() const;
    AMULET_CORE_EXPORT void set_namespace(const std::string& namespace_);

    AMULET_CORE_EXPORT const std::string& get_base_name() const;
    AMULET_CORE_EXPORT void set_base_name(const std::string& base_name);

    AMULET_CORE_EXPORT std::shared_ptr<Amulet::NBT::NamedTag> get_nbt() const;
    AMULET_CORE_EXPORT void set_nbt(std::shared_ptr<Amulet::NBT::NamedTag> nbt);

    AMULET_CORE_EXPORT double get_x() const;
    AMULET_CORE_EXPORT double get_y() const;
    AMULET_CORE_EXPORT double get_z() const;

    AMULET_CORE_EXPORT void set_x(double);
    AMULET_CORE_EXPORT void set_y(double);
    AMULET_CORE_EXPORT void set_z(double);

    AMULET_CORE_EXPORT Entity(
        PlatformType platform,
        VersionNumber version,
        std::string namespace_,
        std::string base_name,
        double x,
        double y,
        double z,
        std::shared_ptr<Amulet::NBT::NamedTag> nbt);

    AMULET_CORE_EXPORT ~Entity();

    AMULET_CORE_EXPORT void serialise(BinaryWriter&) const;
    AMULET_CORE_EXPORT static Entity deserialise(BinaryReader&);

    AMULET_CORE_EXPORT bool operator==(const Entity& other) const;
};
}
