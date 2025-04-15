#include <cstdint>
#include <optional>
#include <string>
#include <unordered_map>
#include <vector>

#include <amulet/chunk/chunk.hpp>
#include <amulet/chunk_components/block_component.hpp>
#include <amulet/dll.hpp>

#include "chunk.hpp"

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
    const BlockStack& default_block,
    const Biome& default_biome)
    : ChunkComponentHelper()
{
    VersionNumber version_number(std::initializer_list<std::int64_t> { -1 });
    VersionRange version_range("java", version_number, version_number);
    JavaRawChunkComponent::init();
    DataVersionComponent::init(-1);
    BlockComponent::init(
        version_range,
        SectionShape(
            static_cast<std::uint16_t>(16),
            static_cast<std::uint16_t>(16),
            static_cast<std::uint16_t>(16)),
        default_block);
}

JavaChunk0::JavaChunk0(
    std::int64_t data_version,
    const BlockStack& default_block,
    const Biome& default_biome)
    : ChunkComponentHelper()
{
    if (data_version < 0 || 1443 < data_version) {
        throw std::invalid_argument("data version must be between 0 and 1443");
    }
    VersionNumber version_number(std::initializer_list<std::int64_t> { data_version });
    VersionRange version_range("java", version_number, version_number);
    JavaRawChunkComponent::init();
    DataVersionComponent::init(data_version);
    BlockComponent::init(
        version_range,
        SectionShape(
            static_cast<std::uint16_t>(16),
            static_cast<std::uint16_t>(16),
            static_cast<std::uint16_t>(16)),
        default_block);
}

JavaChunk1444::JavaChunk1444(
    std::int64_t data_version,
    const BlockStack& default_block,
    const Biome& default_biome)
    : ChunkComponentHelper()
{
    if (data_version < 1444 || 1465 < data_version) {
        throw std::invalid_argument("data version must be between 1443 and 1465");
    }
    VersionNumber version_number(std::initializer_list<std::int64_t> { data_version });
    VersionRange version_range("java", version_number, version_number);
    JavaRawChunkComponent::init();
    DataVersionComponent::init(data_version);
    BlockComponent::init(
        version_range,
        SectionShape(
            static_cast<std::uint16_t>(16),
            static_cast<std::uint16_t>(16),
            static_cast<std::uint16_t>(16)),
        default_block);
}

JavaChunk1466::JavaChunk1466(
    std::int64_t data_version,
    const BlockStack& default_block,
    const Biome& default_biome)
    : ChunkComponentHelper()
{
    if (data_version < 1466 || 2202 < data_version) {
        throw std::invalid_argument("data version must be between 1466 and 2202");
    }
    VersionNumber version_number(std::initializer_list<std::int64_t> { data_version });
    VersionRange version_range("java", version_number, version_number);
    JavaRawChunkComponent::init();
    DataVersionComponent::init(data_version);
    BlockComponent::init(
        version_range,
        SectionShape(
            static_cast<std::uint16_t>(16),
            static_cast<std::uint16_t>(16),
            static_cast<std::uint16_t>(16)),
        default_block);
}

JavaChunk2203::JavaChunk2203(
    std::int64_t data_version,
    const BlockStack& default_block,
    const Biome& default_biome)
    : ChunkComponentHelper()
{
    if (data_version < 2203) {
        throw std::invalid_argument("data version must be at least 2203");
    }
    VersionNumber version_number(std::initializer_list<std::int64_t> { data_version });
    VersionRange version_range("java", version_number, version_number);
    JavaRawChunkComponent::init();
    DataVersionComponent::init(data_version);
    BlockComponent::init(
        version_range,
        SectionShape(
            static_cast<std::uint16_t>(16),
            static_cast<std::uint16_t>(16),
            static_cast<std::uint16_t>(16)),
        default_block);
}

static const ChunkNullConstructor<JavaChunkNA> _jcna;
static const ChunkNullConstructor<JavaChunk0> _jc0;
static const ChunkNullConstructor<JavaChunk1444> _jc1444;
static const ChunkNullConstructor<JavaChunk1466> _jc1466;
static const ChunkNullConstructor<JavaChunk2203> _jc2203;

static std::map<std::string, std::function<std::unique_ptr<JavaChunk>()>> java_chunk_constructors = {
    { JavaChunkNA::ChunkID, []() { return std::make_unique<JavaChunkNA>(); } },
    { JavaChunk0::ChunkID, []() { return std::make_unique<JavaChunk0>(); } },
    { JavaChunk1444::ChunkID, []() { return std::make_unique<JavaChunk1444>(); } },
    { JavaChunk1466::ChunkID, []() { return std::make_unique<JavaChunk1466>(); } },
    { JavaChunk2203::ChunkID, []() { return std::make_unique<JavaChunk2203>(); } },
};

namespace detail {
    std::unique_ptr<JavaChunk> get_java_null_chunk(const std::string& chunk_id)
    {
        auto it = java_chunk_constructors.find(chunk_id);
        if (it == java_chunk_constructors.end()) {
            throw std::runtime_error("Unknown chunk_id " + chunk_id);
        }
        return it->second();
    }
    std::string get_java_chunk_id(const JavaChunk& chunk) {
        std::string chunk_id = chunk.get_chunk_id();
        if (!java_chunk_constructors.contains(chunk_id)) {
            throw std::runtime_error("Unknown chunk_id " + chunk_id);
        }
        return chunk_id;
    }
} // namespace detail

}
