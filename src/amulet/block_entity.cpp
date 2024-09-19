#include <amulet/block_entity.hpp>

namespace Amulet {

	void BlockEntity::serialise(BinaryWriter&) const {
		throw std::runtime_error("NotImplemented");
	}
	std::shared_ptr<BlockEntity> BlockEntity::deserialise(BinaryReader&) {
		throw std::runtime_error("NotImplemented");
	}

}
