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
class Entity : public PlatformVersionContainer {
private:
    std::string _namespace;
    std::string _base_name;
    std::shared_ptr<AmuletNBT::NamedTag> _nbt;
    double _x;
    double _y;
    double _z;

public:
    AMULET_CORE_EXPORT const std::string& get_namespace() const;
    AMULET_CORE_EXPORT void set_namespace(const std::string& namespace_);

    AMULET_CORE_EXPORT const std::string& get_base_name() const;
    AMULET_CORE_EXPORT void set_base_name(const std::string& base_name);

    AMULET_CORE_EXPORT std::shared_ptr<AmuletNBT::NamedTag> get_nbt() const;
    AMULET_CORE_EXPORT void set_nbt(std::shared_ptr<AmuletNBT::NamedTag> nbt);

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
        std::shared_ptr<AmuletNBT::NamedTag> nbt);

    AMULET_CORE_EXPORT ~Entity();

    AMULET_CORE_EXPORT void serialise(BinaryWriter&) const;
    AMULET_CORE_EXPORT static Entity deserialise(BinaryReader&);

    bool operator==(const Entity& other) const
    {
        return (
            PlatformVersionContainer::operator==(other) && _namespace == other._namespace && _base_name == other._base_name && AmuletNBT::NBTTag_eq(*_nbt, *other._nbt));
    }
};
}
