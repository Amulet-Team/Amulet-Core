#include <amulet/core/dll.hpp>
#include <amulet/core/version/version.hpp>

#include "entity.hpp"

namespace Amulet {

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
