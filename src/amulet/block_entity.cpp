#include <amulet/block_entity.hpp>

namespace Amulet {

	void BlockEntity::serialise(Amulet::BinaryWriter&) const {
		throw std::runtime_error("NotImplemented");
	}
	std::shared_ptr<BlockEntity> BlockEntity::deserialise(Amulet::BinaryReader&) {
		throw std::runtime_error("NotImplemented");
	}

}
