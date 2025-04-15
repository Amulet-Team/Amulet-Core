#include <algorithm>
#include <cstdint>
#include <functional>
#include <map>
#include <memory>
#include <optional>
#include <stdexcept>
#include <string>
#include <tuple>
#include <type_traits>
#include <variant>

#include <amulet_nbt/tag/compound.hpp>
#include <amulet_nbt/tag/named_tag.hpp>

#include <amulet/_game/game.hpp>
#include <amulet/block/block.hpp>
#include <amulet/chunk/chunk.hpp>
#include <amulet/version/version.hpp>

#include "chunk.hpp"
#include "long_array.hpp"
#include "raw_dimension.hpp"

using namespace AmuletNBT;

namespace Amulet {
template <typename tagT>
tagT get_tag(const CompoundTag& compound, std::string name, std::function<tagT()> get_default)
{
    const auto& it = compound.find(name);
    if (
        it != compound.end() && std::holds_alternative<tagT>(it->second)) {
        return std::get<tagT>(it->second);
    }
    return get_default();
}

template <typename tagT>
tagT pop_tag(CompoundTag& compound, std::string name, std::function<tagT()> get_default)
{
    auto node = compound.extract(name);
    if (
        node && std::holds_alternative<tagT>(node.mapped())) {
        return std::get<tagT>(node.mapped());
    }
    return get_default();
}

CompoundTagPtr get_region(const JavaRawChunk& raw_chunk)
{
    const auto& it = raw_chunk.find("region");
    if (
        it != raw_chunk.end() && std::holds_alternative<CompoundTagPtr>(it->second.tag_node)) {
        return std::get<CompoundTagPtr>(it->second.tag_node);
    }
    return std::make_shared<CompoundTag>();
}

CompoundTagPtr get_level(const CompoundTag& region)
{
    return get_tag<CompoundTagPtr>(
        region,
        "Level",
        []() { return std::make_shared<CompoundTag>(); });
}

std::int64_t validate_coords(
    CompoundTag& level,
    std::int64_t cx,
    std::int64_t cz)
{
    if (
        pop_tag<IntTag>(level, "xPos", []() { return IntTag(); }).value != cx || pop_tag<IntTag>(level, "zPos", []() { return IntTag(); }).value != cz) {
        throw std::runtime_error("Chunk coord data is incorrect.");
    }
    std::int64_t cy = pop_tag<IntTag>(level, "yPos", []() { return IntTag(); }).value;
    return cy << 4;
}

template <typename chunkT>
void decode_last_update(chunkT& chunk, CompoundTag& level)
{
    // TODO
    // pop_tag<LongTag>(level, "LastUpdate", []() { return LongTag(); }).value;
}

template <typename chunkT>
void decode_inhabited_time(chunkT& chunk, CompoundTag& level)
{
    // TODO
    // pop_tag<LongTag>(level, "InhabitedTime", []() { return LongTag(); }).value;
}

template <typename chunkT>
void decode_terrain_populated(chunkT& chunk, CompoundTag& level)
{
    // TODO
    // pop_tag<ByteTag>(level, "TerrainPopulated", []() { return ByteTag(1); }).value;
}

template <typename chunkT>
void decode_light_populated(chunkT& chunk, CompoundTag& level)
{
    // TODO
    // pop_tag<ByteTag>(level, "LightPopulated", []() { return ByteTag(1); }).value;
}

template <typename chunkT>
void decode_status(chunkT& chunk, CompoundTag& level, std::int64_t data_version)
{
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
void decode_heightmap(chunkT& chunk, CompoundTag& level)
{
    // TODO
}

template <typename chunkT>
void decode_heightmaps_compound(chunkT& chunk, CompoundTag& level)
{
    // TODO
}

template <int DataVersion>
std::unique_ptr<JavaChunk> _decode_java_chunk(
    JavaGameVersion& game_version,
    const JavaRawChunk& raw_chunk,
    CompoundTag& region,
    std::int64_t cx,
    std::int64_t cz,
    const VersionNumber& version,
    std::int64_t data_version,
    const BlockStack& default_block,
    const Biome& default_biome,
    std::function<const Block&()> get_water)
{
    // Validate coordinates
    CompoundTagPtr level_ptr;
    CompoundTag& level = [&]() -> CompoundTag& {
        if constexpr (DataVersion >= 2203) {
            return data_version >= 2844 ? region : *(level_ptr = get_level(region));
        } else {
            level_ptr = get_level(region);
            return *level_ptr;
        }
    }();
    auto floor_y = validate_coords(level, cx, cz);

    // Make the chunk
    auto chunk_ptr = [&]() {
        if constexpr (DataVersion >= 2203) {
            return std::make_unique<JavaChunk2203>(
                data_version,
                default_block,
                default_biome);
        } else if constexpr (DataVersion >= 1466) {
            return std::make_unique<JavaChunk1466>(
                data_version,
                default_block,
                default_biome);
        } else if constexpr (DataVersion >= 1444) {
            return std::make_unique<JavaChunk1444>(
                data_version,
                default_block,
                default_biome);
        } else if constexpr (DataVersion >= 0) {
            return std::make_unique<JavaChunk0>(
                data_version,
                default_block,
                default_biome);
        } else {
            return std::make_unique<JavaChunkNA>(
                default_block,
                default_biome);
        }
    }();
    auto& chunk = *chunk_ptr;

    if constexpr (DataVersion == -1) {
        // LegacyVersionComponent TODO
        // pop_tag<ByteTag>(*level, "V", []() { return ByteTag(1); });
    }

    decode_last_update(chunk, level);
    decode_inhabited_time(chunk, level);

    // Status
    if constexpr (DataVersion >= 1444) {
        decode_status(chunk, level, data_version);
    } else {
        decode_terrain_populated(chunk, level);
        decode_light_populated(chunk, level);
    }

    // Heightmaps
    if constexpr (DataVersion >= 1466) {
        decode_heightmaps_compound(chunk, level);
    } else {
        decode_heightmap(chunk, level);
    }

    // Sections
    ListTagPtr sections_ptr = get_tag<ListTagPtr>(
        level,
        []() { if constexpr (DataVersion >= 2844){ return "sections"; } else { return "Sections"; } }(),
        []() { return std::make_shared<ListTag>(); });
    if (!std::holds_alternative<CompoundListTag>(*sections_ptr)) {
        throw std::invalid_argument("Chunk sections is not a list of compound tags.");
    }
    auto& sections = std::get<CompoundListTag>(*sections_ptr);
    std::map<std::int64_t, CompoundTagPtr> sections_map;
    for (auto& tag : sections) {
        sections_map.emplace(
            get_tag<ByteTag>(*tag, "Y", []() { return ByteTag(); }).value,
            tag);
    }

    // blocks
    auto block_component = chunk.get_block();
    auto block_palette = block_component->get_palette();
    auto block_sections = block_component->get_sections();
    if constexpr (DataVersion >= 1444) {
        // Palette format
        // if data_version >= 2844:
        //     region.sections[].block_states.data
        //     region.sections[].block_states.palette
        // elif data_version >= 2836:
        //     region.Level.Sections[].block_states.data
        //     region.Level.Sections[].block_states.palette
        // else:
        //     region.Level.Sections[].BlockStates
        //     region.Level.Sections[].Palette

        for (auto& [cy, section] : sections_map) {
            auto [palette_tag, data_tag] = [&]() {
                if (data_version >= 2836) {
                    auto block_states_tag = pop_tag<CompoundTagPtr>(*section, "block_states", []() { return std::make_shared<CompoundTag>(); });
                    return std::make_pair(
                        pop_tag<ListTagPtr>(*block_states_tag, "palette", []() { return std::make_shared<ListTag>(); }),
                        pop_tag<LongArrayTagPtr>(*block_states_tag, "data", []() { return std::make_shared<LongArrayTag>(); }));
                } else {
                    return std::make_pair(
                        pop_tag<ListTagPtr>(*section, "Palette", []() { return std::make_shared<ListTag>(); }),
                        pop_tag<LongArrayTagPtr>(*section, "BlockStates", []() { return std::make_shared<LongArrayTag>(); }));
                }
            }();
            if (!std::holds_alternative<CompoundListTag>(*palette_tag)) {
                continue;
            }
            const auto& palette = std::get<CompoundListTag>(*palette_tag);
            size_t palette_size = palette.size();
            std::vector<std::uint32_t> lut;
            lut.reserve(palette_size);
            for (auto& block_tag : palette) {
                auto block_name = get_tag<StringTag>(*block_tag, "Name", []() -> StringTag { throw std::invalid_argument("Block has no Name attribute."); });
                auto colon_index = block_name.find(':');
                auto [block_namespace, block_base_name] = [&]() -> std::pair<std::string, std::string> {
                    if (colon_index == std::string::npos) {
                        return std::make_pair("", block_name);
                    } else {
                        return std::make_pair(
                            block_name.substr(0, colon_index),
                            block_name.substr(colon_index + 1));
                    }
                }();
                auto properties_tag = get_tag<CompoundTagPtr>(*block_tag, "Properties", []() { return std::make_shared<CompoundTag>(); });
                std::map<std::string, PropertyValueType> block_properties;
                for (const auto& [k, v] : *properties_tag) {
                    std::visit([&block_properties, &k](auto&& arg) {
                        using T = std::decay_t<decltype(arg)>;
                        if constexpr (
                            std::is_same_v<T, AmuletNBT::ByteTag> || std::is_same_v<T, AmuletNBT::ShortTag> || std::is_same_v<T, AmuletNBT::IntTag> || std::is_same_v<T, AmuletNBT::LongTag> || std::is_same_v<T, AmuletNBT::StringTag>) {
                            block_properties.emplace(k, arg);
                        }
                    },
                        v);
                }
                std::vector<Block> blocks;

                auto waterloggable = game_version.get_block_data()->is_waterloggable(block_namespace, block_base_name);
                if (waterloggable == Waterloggable::Yes) {
                    auto waterlogged_it = block_properties.find("waterlogged");
                    if (
                        waterlogged_it != block_properties.end() and std::holds_alternative<StringTag>(waterlogged_it->second)) {
                        if (std::get<StringTag>(waterlogged_it->second) == "true") {
                            blocks.push_back(get_water());
                        }
                        block_properties.erase(waterlogged_it);
                    }
                } else if (waterloggable == Waterloggable::Always) {
                    blocks.push_back(get_water());
                }
                blocks.insert(
                    blocks.begin(),
                    Block(
                        "java",
                        version,
                        block_namespace,
                        block_base_name,
                        block_properties));

                lut.push_back(static_cast<std::uint32_t>(block_palette->block_stack_to_index(blocks)));
            }

            block_sections->set_section(
                cy,
                [&] {
                    if (data_tag->empty()) {
                        return std::make_shared<IndexArray3D>(
                            std::make_tuple<std::uint16_t>(16, 16, 16),
                            0);
                    } else {
                        std::vector<std::uint32_t> decoded_vector(4096);
                        std::span<std::uint32_t> decoded_span(decoded_vector);
                        Amulet::decode_long_array(
                            std::span<std::uint64_t>(reinterpret_cast<std::uint64_t*>(data_tag->data()), data_tag->size()),
                            decoded_span,
                            std::max<std::uint8_t>(4, std::bit_width(palette_size - 1)),
                            data_version <= 2529);
                        auto index_array = std::make_shared<IndexArray3D>(
                            std::make_tuple<std::uint16_t>(16, 16, 16));
                        std::span<std::uint32_t> index_array_span(index_array->get_buffer(), index_array->get_size());
                        // Convert YZX to XYZ and look up in lut.
                        for (size_t y = 0; y < 16; y++) {
                            for (size_t x = 0; x < 16; x++) {
                                for (size_t z = 0; z < 16; z++) {
                                    auto& block_index = decoded_span[y * 256 + z * 16 + x];
                                    if (palette_size <= block_index) {
                                        throw std::runtime_error(
                                            "Block index at cx=" + std::to_string(cx) + ",cy=" + std::to_string(cy) + ",cz=" + std::to_string(cx) + ",dx=" + std::to_string(x) + ",dy=" + std::to_string(y) + ",dz=" + std::to_string(z) + " is larger than the block palette size.");
                                    }
                                    index_array_span[x * 256 + y * 16 + z] = lut[block_index];
                                }
                            }
                        }
                        return index_array;
                    }
                }());
        }
    } else {
        // Numerical format
        throw std::runtime_error("NotImplemented");
    }

    // TODO: biomes

    // Return the chunk
    return chunk_ptr;
}

// Get the default block for this dimension and version.
static BlockStack _get_default_block(
    JavaRawDimension& dimension,
    const VersionRange& version_range)
{
    std::vector<Block> blocks;
    for (const auto& block : dimension.get_default_block().get_blocks()) {
        if (version_range.contains(block.get_platform(), block.get_version())) {
            blocks.push_back(block);
        } else {
            auto converted = get_game_version(block.get_platform(), block.get_version())->get_block_data()->translate("java", version_range.get_max_version(), block);
            std::visit(
                [&blocks](auto&& arg) {
                    using T = std::decay_t<decltype(arg)>;
                    if constexpr (std::is_same_v<T, std::tuple<Block, std::optional<BlockEntity>, bool>>) {
                        blocks.emplace_back(std::get<0>(arg));
                    }
                },
                converted);
        }
    }
    if (blocks.empty()) {
        blocks.emplace_back(
            Block(
                version_range.get_platform(),
                version_range.get_max_version(),
                "minecraft",
                "air"));
    }
    return blocks;
}

static Biome _get_default_biome(
    JavaRawDimension& dimension,
    const VersionRange& version_range)
{
    auto& biome = dimension.get_default_biome();
    if (version_range.contains(biome.get_platform(), biome.get_version())) {
        return biome;
    } else {
        return get_game_version(biome.get_platform(), biome.get_version())->get_biome_data()->translate("java", version_range.get_max_version(), biome);
    }
}

std::unique_ptr<JavaChunk> JavaRawDimension::decode_chunk(
    const JavaRawChunk& raw_chunk,
    std::int64_t cx,
    std::int64_t cz)
{
    // Get the region compound tag
    CompoundTagPtr region = get_region(raw_chunk);

    std::int64_t data_version = pop_tag<IntTag>(
        *region,
        "DataVersion",
        []() { return IntTag(-1); }).value;

    VersionNumber version(std::initializer_list<std::int64_t> { data_version });
    auto version_range = std::make_shared<VersionRange>("java", version, version);
    auto default_block = _get_default_block(*this, *version_range);
    auto default_biome = _get_default_biome(*this, *version_range);
    std::shared_ptr<JavaGameVersion> game_version = get_java_game_version(version);

    std::optional<Block> _water_block;
    auto get_water = [&version, &_water_block]() -> const Block& {
        if (!_water_block) {
            auto converted = get_java_game_version(VersionNumber({ 3837 }))->get_block_data()->translate("java", version, Block("java", VersionNumber({ 3837 }), "minecraft", "water", std::initializer_list<BlockProperites::value_type> { { "level", StringTag("0") } }));
            std::visit(
                [&version, &_water_block](auto&& arg) {
                    using T = std::decay_t<decltype(arg)>;
                    if constexpr (std::is_same_v<T, std::tuple<Block, std::optional<BlockEntity>, bool>>) {
                        _water_block = std::get<0>(arg);
                    } else {
                        throw std::runtime_error("Water block did not convert to a block in version Java " + version.toString());
                    }
                },
                converted);
        }
        return *_water_block;
    };

    if (data_version >= 2203) {
        return _decode_java_chunk<2203>(*game_version, raw_chunk, *region, cx, cz, version, data_version, default_block, default_biome, get_water);
    } else if (data_version >= 1466) {
        return _decode_java_chunk<1466>(*game_version, raw_chunk, *region, cx, cz, version, data_version, default_block, default_biome, get_water);
    } else if (data_version >= 1444) {
        return _decode_java_chunk<1444>(*game_version, raw_chunk, *region, cx, cz, version, data_version, default_block, default_biome, get_water);
    } else if (data_version >= 0) {
        return _decode_java_chunk<0>(*game_version, raw_chunk, *region, cx, cz, version, data_version, default_block, default_biome, get_water);
    } else {
        return _decode_java_chunk<-1>(*game_version, raw_chunk, *region, cx, cz, version, data_version, default_block, default_biome, get_water);
    }
}

} // namespace Amulet
