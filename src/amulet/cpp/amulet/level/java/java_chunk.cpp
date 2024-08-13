#include <string>
#include <optional>
#include <vector>
#include <unordered_map>
#include <cstdint>

#include <amulet/chunk.hpp>
#include <amulet/level/java/java_chunk.hpp>
#include <amulet/chunk_components/block_component.hpp>

namespace Amulet {
	// JavaChunk
	const std::string JavaChunkNA::ChunkID = "Amulet::JavaChunkNA";
	
	std::string JavaChunkNA::chunk_id() { return ChunkID; }
	
	JavaChunkNA::JavaChunkNA(
		std::int64_t data_version,
		std::shared_ptr<BlockStack> default_block
	) : ChunkComponentHelper() {
		auto version_number = std::make_shared<VersionNumber>(
			std::initializer_list<std::int64_t>{ data_version }
		);
		auto version_range = std::make_shared<VersionRange>(
			"java",
			version_number,
			version_number
		);
		BlockComponent::init(
			version_range,
			SectionShape(
				static_cast<std::uint16_t>(16),
				static_cast<std::uint16_t>(16),
				static_cast<std::uint16_t>(16)
			),
			default_block
		);
	}

	static const ChunkNullConstructor<JavaChunkNA> java_chunk_reconstructor;
}
