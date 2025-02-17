#include <amulet/block_entity.hpp>
#include <amulet/dll.hpp>

namespace Amulet {

void BlockEntity::serialise(BinaryWriter&) const
{
    throw std::runtime_error("NotImplemented");
}
BlockEntity BlockEntity::deserialise(BinaryReader&)
{
    throw std::runtime_error("NotImplemented");
}

}
