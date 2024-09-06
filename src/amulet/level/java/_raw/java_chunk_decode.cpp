#include <memory>
#include <map>
#include <cstdint>
#include <stdexcept>
#include <type_traits>
#include <string>
#include <functional>
#include <variant>

#include <pybind11/pybind11.h>

#include <amulet_nbt/tag/named_tag.hpp>
#include <amulet_nbt/tag/compound.hpp>

#include <amulet/version.hpp>
#include <amulet/block.hpp>
#include <amulet/chunk.hpp>
#include <amulet/level/java/java_chunk.hpp>

namespace py = pybind11;
using namespace AmuletNBT;

namespace Amulet {
	template <typename tagT>
	tagT get_tag(const CompoundTag& compound, std::string name, std::function<tagT()> get_default) {
		const auto& it = compound.find(name);
		if (
			it != compound.end() &&
			std::holds_alternative<tagT>(it->second)
			) {
			return std::get<tagT>(it->second);
		}
		return get_default();
	}

	template <typename tagT>
	tagT pop_tag(CompoundTag& compound, std::string name, std::function<tagT()> get_default) {
		auto node = compound.extract(name);
		if (
			node &&
			std::holds_alternative<tagT>(node.mapped())
			) {
			return std::get<tagT>(node.mapped());
		}
		return get_default();
	}

	CompoundTagPtr get_region(const std::map<std::string, NamedTag>& raw_chunk) {
		const auto& it = raw_chunk.find("region");
		if (
			it != raw_chunk.end() &&
			std::holds_alternative<CompoundTagPtr>(it->second.tag_node)
			) {
			return std::get<CompoundTagPtr>(it->second.tag_node);
		}
		return std::make_shared<CompoundTag>();
	}

	CompoundTagPtr get_level(const CompoundTag& region) {
		return get_tag<CompoundTagPtr>(
			region,
			"Level",
			[]() { return std::make_shared<CompoundTag>(); }
		);
	}

	std::int64_t validate_coords(
		CompoundTag& level,
		std::int64_t cx,
		std::int64_t cz
	) {
		if (
			pop_tag<IntTag>(level, "xPos", []() { return IntTag(); }).value != cx ||
			pop_tag<IntTag>(level, "zPos", []() { return IntTag(); }).value != cz
			) {
			throw std::runtime_error("Chunk coord data is incorrect.");
		}
		std::int64_t cy = pop_tag<IntTag>(level, "yPos", []() { return IntTag(); }).value;
		return cy << 4;
	}

	template <typename chunkT>
	void decode_last_update(chunkT& chunk, CompoundTag& level) {
		// TODO
		//pop_tag<LongTag>(level, "LastUpdate", []() { return LongTag(); }).value;
	}

	template <typename chunkT>
	void decode_inhabited_time(chunkT& chunk, CompoundTag& level) {
		// TODO
		//pop_tag<LongTag>(level, "InhabitedTime", []() { return LongTag(); }).value;
	}

	template <typename chunkT>
	void decode_terrain_populated(chunkT& chunk, CompoundTag& level) {
		// TODO
		//pop_tag<ByteTag>(level, "TerrainPopulated", []() { return ByteTag(1); }).value;
	}

	template <typename chunkT>
	void decode_light_populated(chunkT& chunk, CompoundTag& level) {
		// TODO
		//pop_tag<ByteTag>(level, "LightPopulated", []() { return ByteTag(1); }).value;
	}

	template <typename chunkT>
	void decode_status(chunkT& chunk, CompoundTag& level, std::int64_t data_version) {
		// TODO
		/*std::string status = pop_tag<StringTag>(level, "Status", []() { return StringTag(); });
		if (!status.empty()) {
			chunk.set_status(status);
		}
		else if (data_version >= 3454) {
			chunk.set_status("minecraft:full");
		}
		else if (data_version >= 1912) {
			chunk.set_status("full");
		}
		else {
			chunk.set_status("postprocessed");
		}*/
	}

	template <typename chunkT>
	void decode_heightmap(chunkT& chunk, CompoundTag& level) {
		// TODO
	}

	template <typename chunkT>
	void decode_heightmaps_compound(chunkT& chunk, CompoundTag& level) {
		// TODO
	}

	template <int DataVersion>
	std::shared_ptr<
		std::conditional_t<DataVersion >= 2203, JavaChunk2203,
		std::conditional_t<DataVersion >= 1466, JavaChunk1466,
		std::conditional_t<DataVersion >= 1444, JavaChunk1444,
		std::conditional_t<DataVersion >= 0, JavaChunk0,
		JavaChunkNA
		>>>>
	> _decode_java_chunk(
		std::map<std::string, NamedTag>& raw_chunk,
		CompoundTag& region,
		std::int64_t cx,
		std::int64_t cz,
		std::int64_t data_version,
		std::shared_ptr<BlockStack> default_block,
		std::shared_ptr<Biome> default_biome
	) {
		// Validate coordinates
		CompoundTagPtr level_ptr;
		CompoundTag& level = [&]() -> CompoundTag& {
			if constexpr (DataVersion >= 2203) {
				return data_version >= 2844 ? region : *(level_ptr = get_level(region));
			}
			else {
				level_ptr = get_level(region);
				return *level_ptr;

			}
		}();
		auto floor_y = validate_coords(level, cx, cz);

		// Make the chunk
		auto chunk_ptr = [&]() {
			if constexpr (DataVersion >= 2203) {
				return std::make_shared<JavaChunk2203>(
					data_version,
					default_block,
					default_biome
					);
			}
			else if constexpr (DataVersion >= 1466) {
				return std::make_shared<JavaChunk1466>(
					data_version,
					default_block,
					default_biome
					);
			}
			else if constexpr (DataVersion >= 1444) {
				return std::make_shared<JavaChunk1444>(
					data_version,
					default_block,
					default_biome
					);
			}
			else if constexpr (DataVersion >= 0) {
				return std::make_shared<JavaChunk0>(
					data_version,
					default_block,
					default_biome
					);
			}
			else {
				return std::make_shared<JavaChunkNA>(
					default_block,
					default_biome
					);
			}
		}();
		auto& chunk = *chunk_ptr;

		if constexpr (DataVersion == -1) {
			// LegacyVersionComponent TODO
			//pop_tag<ByteTag>(*level, "V", []() { return ByteTag(1); });
		}

		decode_last_update(chunk, level);
		decode_inhabited_time(chunk, level);

		// Status
		if constexpr (DataVersion >= 1444) {
			decode_status(chunk, level, data_version);
		}
		else {
			decode_terrain_populated(chunk, level);
			decode_light_populated(chunk, level);
		}

		// Heightmaps
		if constexpr (DataVersion >= 1466) {
			decode_heightmaps_compound(chunk, level);
		}
		else {
			decode_heightmap(chunk, level);
		}

		// Return the chunk
		return chunk_ptr;
	}


	// Get the default block for this dimension and version via the python API.
	std::shared_ptr<BlockStack> get_default_block(
		py::object dimension,
		const VersionRange& version_range
	) {
		auto default_block = dimension.attr("default_block")().cast<std::shared_ptr<BlockStack>>();
		std::vector<std::shared_ptr<Block>> blocks;
		for (const auto& block : default_block->get_blocks()) {
			if (version_range.contains(block->get_platform(), *block->get_version())) {
				blocks.push_back(block);
			}
			else {
				py::object block_ = py::module::import("amulet.game").attr("get_game_version")(
					py::cast(block->get_platform()),
					py::cast(block->get_version())
					).attr("block").attr("translate")(
						"java",
						py::cast(version_range.get_max_version()),
						py::cast(block)
						).attr("__getitem__")(0);
				if (py::isinstance<Block>(block_)) {
					blocks.push_back(block_.cast<std::shared_ptr<Block>>());
				}
			}
		}
		if (blocks.empty()) {
			blocks.push_back(
				std::make_shared<Block>(
					version_range.get_platform(),
					version_range.get_max_version(),
					"minecraft",
					"air"
					)
			);
		}
		return std::make_shared<BlockStack>(blocks);
	}

	std::shared_ptr<Biome> get_default_biome(
		py::object dimension,
		const VersionRange& version_range
	) {
		auto biome = dimension.attr("default_biome")().cast<std::shared_ptr<Biome>>();
		if (version_range.contains(biome->get_platform(), *biome->get_version())) {
			return biome;
		}
		else {
			return py::module::import("amulet.game").attr("get_game_version")(
				py::cast(biome->get_platform()),
				py::cast(biome->get_version())
				).attr("biome").attr("translate")(
					"java",
					py::cast(version_range.get_max_version()),
					py::cast(biome)
					).cast<std::shared_ptr<Biome>>();
		}
	}

	std::shared_ptr<JavaChunk> decode_java_chunk(
		py::object raw_level,
		py::object dimension,
		std::map<std::string, NamedTag>& raw_chunk,
		std::int64_t cx,
		std::int64_t cz
	) {
		// Get the region compound tag
		CompoundTagPtr region = get_region(raw_chunk);

		std::int64_t data_version = pop_tag<IntTag>(
			*region,
			"DataVersion",
			[]() { return IntTag(-1); }
		).value;

		auto version = std::make_shared<VersionNumber>(std::initializer_list<std::int64_t>{ data_version });
		auto version_range = std::make_shared<VersionRange>("java", version, version);
		auto default_block = get_default_block(dimension, *version_range);
		auto default_biome = get_default_biome(dimension, *version_range);

		if (data_version >= 2203) {
			return _decode_java_chunk<2203>(raw_chunk, *region, cx, cz, data_version, default_block, default_biome);
		}
		else if (data_version >= 1466) {
			return _decode_java_chunk<1466>(raw_chunk, *region, cx, cz, data_version, default_block, default_biome);
		}
		else if (data_version >= 1444) {
			return _decode_java_chunk<1444>(raw_chunk, *region, cx, cz, data_version, default_block, default_biome);
		}
		else if (data_version >= 0) {
			return _decode_java_chunk<0>(raw_chunk, *region, cx, cz, data_version, default_block, default_biome);
		}
		else {
			return _decode_java_chunk<-1>(raw_chunk, *region, cx, cz, data_version, default_block, default_biome);
		}
	}
}
