#include <amulet/dll.hpp>
#include <amulet/block_entity.hpp>

namespace Amulet {

	AMULET_CORE_DLLX void BlockEntity::serialise(BinaryWriter&) const {
		throw std::runtime_error("NotImplemented");
	}
	AMULET_CORE_DLLX std::shared_ptr<BlockEntity> BlockEntity::deserialise(BinaryReader&) {
		throw std::runtime_error("NotImplemented");
	}

}
