#include <amulet/dll.hpp>

#include "block_entity.hpp"

namespace Amulet {

const std::string& BlockEntity::get_namespace() const { return _namespace; }

void BlockEntity::set_namespace(const std::string& namespace_) { _namespace = namespace_; }

const std::string& BlockEntity::get_base_name() const { return _base_name; }

void BlockEntity::set_base_name(const std::string& base_name) { _base_name = base_name; }

std::shared_ptr<AmuletNBT::NamedTag> BlockEntity::get_nbt() const { return _nbt; }

void BlockEntity::set_nbt(std::shared_ptr<AmuletNBT::NamedTag> nbt) { _nbt = nbt; }

BlockEntity::BlockEntity(
    const PlatformType& platform,
    const VersionNumber& version,
    const std::string& namespace_,
    const std::string& base_name,
    std::shared_ptr<AmuletNBT::NamedTag> nbt)
    : PlatformVersionContainer(platform, version)
    , _namespace(namespace_)
    , _base_name(base_name)
    , _nbt(nbt)
{
}

void BlockEntity::serialise(BinaryWriter&) const
{
    throw std::runtime_error("NotImplemented");
}

BlockEntity BlockEntity::deserialise(BinaryReader&)
{
    throw std::runtime_error("NotImplemented");
}

bool BlockEntity::operator==(const BlockEntity& other) const
{
    return (
        PlatformVersionContainer::operator==(other)
        && _namespace == other._namespace
        && _base_name == other._base_name
        && AmuletNBT::NBTTag_eq(*_nbt, *other._nbt));
}

}
