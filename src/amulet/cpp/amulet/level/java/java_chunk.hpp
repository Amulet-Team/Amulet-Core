#pragma once

#include <string>
#include <optional>
#include <stdexcept>
#include <vector>
#include <amulet/chunk.hpp>
#include <amulet/chunk_components/block_component.hpp>

namespace Amulet {
	class JavaChunkNA : public ChunkComponentHelper<BlockComponent> {
	public:
		static const std::string ChunkID;

		std::string chunk_id();

		using ChunkComponentHelper::ChunkComponentHelper;
		JavaChunkNA(
			std::int64_t data_version,
			std::shared_ptr<BlockStack> default_block
		);
	};
}
