#include <amulet/core/dll.hpp>

#include "block_entity.hpp"

namespace Amulet {

void BlockEntity::serialise(BinaryWriter&) const
{
    throw std::runtime_error("NotImplementedError");
}

BlockEntity BlockEntity::deserialise(BinaryReader&)
{
    throw std::runtime_error("NotImplementedError");
}

bool BlockEntity::operator==(const BlockEntity& other) const
{
    return (
        PlatformVersionContainer::operator==(other)
        && _namespace == other._namespace
        && _base_name == other._base_name
        && Amulet::NBT::NBTTag_eq(*_nbt, *other._nbt));
}

}
