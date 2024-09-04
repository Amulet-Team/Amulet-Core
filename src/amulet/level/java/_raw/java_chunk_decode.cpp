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

template <typename tagT>
tagT get_tag(const AmuletNBT::CompoundTag& compound, std::string name, std::function<tagT()> get_default) {
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
tagT pop_tag(AmuletNBT::CompoundTag& compound, std::string name, std::function<tagT()> get_default) {
	auto node = compound.extract(name);
	if (
		node &&
		std::holds_alternative<tagT>(node.mapped())
	) {
		return std::get<tagT>(node.mapped());
	}
	return get_default();
}

AmuletNBT::CompoundTagPtr get_region(const std::map<std::string, AmuletNBT::NamedTag>& raw_chunk) {
	const auto& it = raw_chunk.find("region");
	if (
		it != raw_chunk.end() &&
		std::holds_alternative<AmuletNBT::CompoundTagPtr>(it->second.tag_node)
		) {
		return std::get<AmuletNBT::CompoundTagPtr>(it->second.tag_node);
	}
	return std::make_shared<AmuletNBT::CompoundTag>();
}

AmuletNBT::CompoundTagPtr get_level(const AmuletNBT::CompoundTag& region) {
	return get_tag<AmuletNBT::CompoundTagPtr>(
		region,
		"Level",
		[]() { return std::make_shared<AmuletNBT::CompoundTag>(); }
	);
}

//// Get the level tag. This may not exist.
//AmuletNBT::CompoundTagPtr level = get_level(*region);
//throw std::runtime_error("");
std::shared_ptr<Amulet::JavaChunkNA> decode_java_chunk_na(
	std::shared_ptr<Amulet::BlockStack> default_block,
	std::shared_ptr<Amulet::Biome> default_biome
) {
	auto chunk = std::make_shared<Amulet::JavaChunkNA>(
		default_block,
		default_biome
	);
	return chunk;
}
std::shared_ptr<Amulet::JavaChunk0> decode_java_chunk_0(
	std::int64_t data_version,
	std::shared_ptr<Amulet::BlockStack> default_block,
	std::shared_ptr<Amulet::Biome> default_biome
) {
	auto chunk = std::make_shared<Amulet::JavaChunk0>(
		data_version,
		default_block,
		default_biome
	);
	return chunk;
}
std::shared_ptr<Amulet::JavaChunk1444> decode_java_chunk_1444(
	std::int64_t data_version,
	std::shared_ptr<Amulet::BlockStack> default_block,
	std::shared_ptr<Amulet::Biome> default_biome
) {
	auto chunk = std::make_shared<Amulet::JavaChunk1444>(
		data_version,
		default_block,
		default_biome
	);
	return chunk;
}
std::shared_ptr<Amulet::JavaChunk1466> decode_java_chunk_1466(
	std::int64_t data_version,
	std::shared_ptr<Amulet::BlockStack> default_block,
	std::shared_ptr<Amulet::Biome> default_biome
) {
	auto chunk = std::make_shared<Amulet::JavaChunk1466>(
		data_version,
		default_block,
		default_biome
	);
	return chunk;
}
std::shared_ptr<Amulet::JavaChunk2203> decode_java_chunk_2203(
	std::int64_t data_version,
	std::shared_ptr<Amulet::BlockStack> default_block,
	std::shared_ptr<Amulet::Biome> default_biome
) {
	auto chunk = std::make_shared<Amulet::JavaChunk2203>(
		data_version,
		default_block,
		default_biome
	);
	return chunk;
}


// Get the default block for this dimension and version via the python API.
std::shared_ptr<Amulet::BlockStack> get_default_block(
	py::object dimension,
	const Amulet::VersionRange& version_range
) {
	auto default_block = dimension.attr("default_block")().cast<std::shared_ptr<Amulet::BlockStack>>();
	std::vector<std::shared_ptr<Amulet::Block>> blocks;
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
			).attr("__getattr__")(0);
			if (py::isinstance<Amulet::Block>(block_)) {
				blocks.push_back(block_.cast<std::shared_ptr<Amulet::Block>>());
			}
		}
	}
	if (blocks.empty()) {
		blocks.push_back(
			std::make_shared<Amulet::Block>(
				version_range.get_platform(),
				version_range.get_max_version(),
				"minecraft",
				"air"
			)
		);
	}
	return std::make_shared<Amulet::BlockStack>(blocks);
}

std::shared_ptr<Amulet::Biome> get_default_biome(
	py::object dimension,
	const Amulet::VersionRange& version_range
) {
	auto biome = dimension.attr("default_biome")().cast<std::shared_ptr<Amulet::Biome>>();
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
		).cast<std::shared_ptr<Amulet::Biome>>();
	}
}


namespace Amulet {
	std::shared_ptr<Amulet::JavaChunk> decode_java_chunk(
		py::object raw_level,
		py::object dimension,
		std::map<std::string, AmuletNBT::NamedTag> raw_chunk,
		std::int64_t cx,
		std::int64_t cz
	) {
		// Get the region compound tag
		AmuletNBT::CompoundTagPtr region = get_region(raw_chunk);

		std::int64_t data_version = pop_tag<AmuletNBT::IntTag>(
			*region, 
			"DataVersion", 
			[]() { return AmuletNBT::IntTag(); }
		).value;

		auto version = std::make_shared<Amulet::VersionNumber>(std::initializer_list<std::int64_t>{ data_version });
		auto version_range = std::make_shared<Amulet::VersionRange>("java", version, version);
		auto default_block = get_default_block(dimension, *version_range);
		auto default_biome = get_default_biome(dimension, *version_range);

		if (data_version >= 2203) {
			return decode_java_chunk_2203(data_version, default_block, default_biome);
		}
		else if (data_version >= 1466) {
			return decode_java_chunk_1466(data_version, default_block, default_biome);
		}
		else if (data_version >= 1444) {
			return decode_java_chunk_1444(data_version, default_block, default_biome);
		}
		else if (data_version >= 0) {
			return decode_java_chunk_0(data_version, default_block, default_biome);
		}
		else {
			return decode_java_chunk_na(default_block, default_biome);
		}
	}
}
