#pragma once

#include <string>
#include <optional>
#include <stdexcept>
#include <vector>
#include <amulet/block.hpp>
#include <amulet/biome.hpp>
#include <amulet/chunk.hpp>
#include <amulet/chunk_components/block_component.hpp>
#include "chunk_components/java_raw_chunk_component.hpp"
#include "chunk_components/data_version_component.hpp"

namespace Amulet {
	class JavaChunk : public Chunk {};

	class JavaChunkNA : public ChunkComponentHelper<
		JavaChunk,
		JavaRawChunkComponent,
		DataVersionComponent,
		// LastUpdateComponent,
		// JavaLegacyVersionComponent,
		BlockComponent//,
		// BlockEntityComponent,
		// EntityComponent,
		// Biome2DComponent,
		// Height2DComponent,
	> {
	public:
		static const std::string ChunkID;

		std::string get_chunk_id() const override;

		using ChunkComponentHelper::ChunkComponentHelper;
		JavaChunkNA(
			std::shared_ptr<BlockStack> default_block,
			std::shared_ptr<Biome> default_biome
		);
	};

	class JavaChunk0 : public ChunkComponentHelper<
		JavaChunk,
		JavaRawChunkComponent,
		DataVersionComponent,
		// LastUpdateComponent,
		// TerrainPopulatedComponent,
		// LightPopulatedComponent,
		BlockComponent//,
		// BlockEntityComponent,
		// EntityComponent,
		// Biome2DComponent,
		// Height2DComponent,
	> {
	public:
		static const std::string ChunkID;

		std::string get_chunk_id() const override;

		using ChunkComponentHelper::ChunkComponentHelper;
		JavaChunk0(
			std::int64_t data_version,
			std::shared_ptr<BlockStack> default_block,
			std::shared_ptr<Biome> default_biome
		);
	};

	class JavaChunk1444 : public ChunkComponentHelper<
		JavaChunk,
		JavaRawChunkComponent,
		DataVersionComponent,
		// LastUpdateComponent,
		// StatusStringComponent,
		BlockComponent//,
		// BlockEntityComponent,
		// EntityComponent,
		// Biome2DComponent,
		// Height2DComponent,
	> {
	public:
		static const std::string ChunkID;

		std::string get_chunk_id() const override;

		using ChunkComponentHelper::ChunkComponentHelper;
		JavaChunk1444(
			std::int64_t data_version,
			std::shared_ptr<BlockStack> default_block,
			std::shared_ptr<Biome> default_biome
		);
	};

	class JavaChunk1466 : public ChunkComponentHelper<
		JavaChunk,
		JavaRawChunkComponent,
		DataVersionComponent,
		// LastUpdateComponent,
		// StatusStringComponent,
		BlockComponent//,
		// BlockEntityComponent,
		// EntityComponent,
		// Biome2DComponent,
		// NamedHeight2DComponent,
	> {
	public:
		static const std::string ChunkID;

		std::string get_chunk_id() const override;

		using ChunkComponentHelper::ChunkComponentHelper;
		JavaChunk1466(
			std::int64_t data_version,
			std::shared_ptr<BlockStack> default_block,
			std::shared_ptr<Biome> default_biome
		);
	};

	class JavaChunk2203 : public ChunkComponentHelper<
		JavaChunk,
		JavaRawChunkComponent,
		DataVersionComponent,
		// LastUpdateComponent,
		// StatusStringComponent,
		BlockComponent//,
		// BlockEntityComponent,
		// EntityComponent,
		// Biome3DComponent,
		// NamedHeight2DComponent,
	> {
	public:
		static const std::string ChunkID;

		std::string get_chunk_id() const override;

		using ChunkComponentHelper::ChunkComponentHelper;
		JavaChunk2203(
			std::int64_t data_version,
			std::shared_ptr<BlockStack> default_block,
			std::shared_ptr<Biome> default_biome
		);
	};
}
