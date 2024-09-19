#include <string>
#include <optional>
#include <vector>
#include <unordered_map>
#include <cstdint>

#include <amulet/chunk.hpp>
#include <amulet/level/java/java_chunk.hpp>
#include <amulet/chunk_components/block_component.hpp>

namespace Amulet {
	const std::string JavaChunkNA::ChunkID = "Amulet::JavaChunkNA";
	const std::string JavaChunk0::ChunkID = "Amulet::JavaChunk0";
	const std::string JavaChunk1444::ChunkID = "Amulet::JavaChunk1444";
	const std::string JavaChunk1466::ChunkID = "Amulet::JavaChunk1466";
	const std::string JavaChunk2203::ChunkID = "Amulet::JavaChunk2203";
	
	std::string JavaChunkNA::get_chunk_id() const { return ChunkID; }
	std::string JavaChunk0::get_chunk_id() const { return ChunkID; }
	std::string JavaChunk1444::get_chunk_id() const { return ChunkID; }
	std::string JavaChunk1466::get_chunk_id() const { return ChunkID; }
	std::string JavaChunk2203::get_chunk_id() const { return ChunkID; }
	
	JavaChunkNA::JavaChunkNA(
		std::shared_ptr<BlockStack> default_block,
		std::shared_ptr<Biome> default_biome
	) : ChunkComponentHelper() {
		auto version_number = std::make_shared<VersionNumber>(
			std::initializer_list<std::int64_t>{ -1 }
		);
		auto version_range = std::make_shared<VersionRange>(
			"java",
			version_number,
			version_number
		);
		JavaRawChunkComponent::init();
		DataVersionComponent::init(-1);
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

	JavaChunk0::JavaChunk0(
		std::int64_t data_version,
		std::shared_ptr<BlockStack> default_block,
		std::shared_ptr<Biome> default_biome
	) : ChunkComponentHelper() {
		if (data_version < 0 || 1443 < data_version) {
			throw std::invalid_argument("data version must be between 0 and 1443");
		}
		auto version_number = std::make_shared<VersionNumber>(
			std::initializer_list<std::int64_t>{ data_version }
		);
		auto version_range = std::make_shared<VersionRange>(
			"java",
			version_number,
			version_number
			);
		JavaRawChunkComponent::init();
		DataVersionComponent::init(data_version);
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

	JavaChunk1444::JavaChunk1444(
		std::int64_t data_version,
		std::shared_ptr<BlockStack> default_block,
		std::shared_ptr<Biome> default_biome
	) : ChunkComponentHelper() {
		if (data_version < 1444 || 1465 < data_version) {
			throw std::invalid_argument("data version must be between 1443 and 1465");
		}
		auto version_number = std::make_shared<VersionNumber>(
			std::initializer_list<std::int64_t>{ data_version }
		);
		auto version_range = std::make_shared<VersionRange>(
			"java",
			version_number,
			version_number
			);
		JavaRawChunkComponent::init();
		DataVersionComponent::init(data_version);
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

	JavaChunk1466::JavaChunk1466(
		std::int64_t data_version,
		std::shared_ptr<BlockStack> default_block,
		std::shared_ptr<Biome> default_biome
	) : ChunkComponentHelper() {
		if (data_version < 1466 || 2202 < data_version) {
			throw std::invalid_argument("data version must be between 1466 and 2202");
		}
		auto version_number = std::make_shared<VersionNumber>(
			std::initializer_list<std::int64_t>{ data_version }
		);
		auto version_range = std::make_shared<VersionRange>(
			"java",
			version_number,
			version_number
			);
		JavaRawChunkComponent::init();
		DataVersionComponent::init(data_version);
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

	JavaChunk2203::JavaChunk2203(
		std::int64_t data_version,
		std::shared_ptr<BlockStack> default_block,
		std::shared_ptr<Biome> default_biome
	) : ChunkComponentHelper() {
		if (data_version < 2203) {
			throw std::invalid_argument("data version must be at least 2203");
		}
		auto version_number = std::make_shared<VersionNumber>(
			std::initializer_list<std::int64_t>{ data_version }
		);
		auto version_range = std::make_shared<VersionRange>(
			"java",
			version_number,
			version_number
			);
		JavaRawChunkComponent::init();
		DataVersionComponent::init(data_version);
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

	static const ChunkNullConstructor<JavaChunkNA> _jcna;
	static const ChunkNullConstructor<JavaChunk0> _jc0;
	static const ChunkNullConstructor<JavaChunk1444> _jc1444;
	static const ChunkNullConstructor<JavaChunk1466> _jc1466;
	static const ChunkNullConstructor<JavaChunk2203> _jc2203;
}
