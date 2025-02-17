#pragma once

#include <cstdint>
#include <map>
#include <memory>
#include <optional>
#include <tuple>

#include <amulet/block_entity.hpp>
#include <amulet/dll.hpp>
#include <amulet/version.hpp>

namespace Amulet {
typedef std::tuple<std::uint16_t, std::int64_t, std::uint16_t> BlockEntityChunkCoord;
class BlockEntityComponentData : public VersionRangeContainer {
private:
    std::uint16_t _x_size;
    std::uint16_t _z_size;
    std::map<
        BlockEntityChunkCoord,
        std::shared_ptr<BlockEntity>>
        _block_entities;

public:
    AMULET_CORE_EXPORT BlockEntityComponentData(
        const VersionRange& version_range,
        std::uint16_t x_size,
        std::uint16_t z_size);

    AMULET_CORE_EXPORT std::uint16_t get_x_size() const;
    AMULET_CORE_EXPORT std::uint16_t get_z_size() const;

    AMULET_CORE_EXPORT const std::map<
        BlockEntityChunkCoord,
        std::shared_ptr<BlockEntity>>&
    get_block_entities() const;

    AMULET_CORE_EXPORT size_t get_size() const;

    AMULET_CORE_EXPORT bool contains(
        const BlockEntityChunkCoord& coord) const;

    AMULET_CORE_EXPORT std::shared_ptr<BlockEntity> get(
        const BlockEntityChunkCoord& coord) const;

    AMULET_CORE_EXPORT void set(
        const BlockEntityChunkCoord& coord,
        std::shared_ptr<BlockEntity> block_entity);

    AMULET_CORE_EXPORT void del(
        const BlockEntityChunkCoord& coord);
};

class BlockEntityComponent {
private:
    std::optional<std::shared_ptr<BlockEntityComponentData>> _value;

protected:
    // Null constructor
    AMULET_CORE_EXPORT BlockEntityComponent() = default;
    // Default constructor
    AMULET_CORE_EXPORT void init(
        const VersionRange& version_range,
        std::uint16_t x_size,
        std::uint16_t z_size);

    // Serialise the component data
    AMULET_CORE_EXPORT std::optional<std::string> serialise() const;
    // Deserialise the component
    AMULET_CORE_EXPORT void deserialise(std::optional<std::string>);

public:
    AMULET_CORE_EXPORT static const std::string ComponentID;
    AMULET_CORE_EXPORT std::shared_ptr<BlockEntityComponentData> get_block_entity();
    AMULET_CORE_EXPORT void set_block_entity(std::shared_ptr<BlockEntityComponentData> component);
};
}
