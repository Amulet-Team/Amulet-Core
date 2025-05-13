#include <amulet/core/dll.hpp>
#include <amulet/core/version/version.hpp>

#include "entity.hpp"

namespace Amulet {

const std::string& Entity::get_namespace() const { return _namespace; }

void Entity::set_namespace(const std::string& namespace_) { _namespace = namespace_; }

const std::string& Entity::get_base_name() const { return _base_name; }

void Entity::set_base_name(const std::string& base_name) { _base_name = base_name; }

std::shared_ptr<Amulet::NBT::NamedTag> Entity::get_nbt() const { return _nbt; }

void Entity::set_nbt(std::shared_ptr<Amulet::NBT::NamedTag> nbt) { _nbt = nbt; }

double Entity::get_x() const { return _x; }

double Entity::get_y() const { return _y; }

double Entity::get_z() const { return _z; }

void Entity::set_x(double x) { _x = x; }

void Entity::set_y(double y) { _y = y; }

void Entity::set_z(double z) { _z = z; }

Entity::Entity(
    PlatformType platform,
    VersionNumber version,
    std::string namespace_,
    std::string base_name,
    double x,
    double y,
    double z,
    std::shared_ptr<Amulet::NBT::NamedTag> nbt)
    : PlatformVersionContainer(std::move(platform), std::move(version))
    , _namespace(std::move(namespace_))
    , _base_name(std::move(base_name))
    , _nbt(std::move(nbt))
    , _x(x)
    , _y(y)
    , _z(z)
{
}

Entity::~Entity() { }

void Entity::serialise(BinaryWriter&) const
{
    throw std::runtime_error("NotImplementedError");
}
Entity Entity::deserialise(BinaryReader&)
{
    throw std::runtime_error("NotImplementedError");
}

bool Entity::operator==(const Entity& other) const
{
    return (
        PlatformVersionContainer::operator==(other)
        && _namespace == other._namespace
        && _base_name == other._base_name
        && _x == other._x
        && _y == other._y
        && _z == other._z
        && Amulet::NBT::NBTTag_eq(*_nbt, *other._nbt));
}

} // namespace Amulet
