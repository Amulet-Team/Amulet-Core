#pragma once

#include <cstdint>
#include <map>
#include <memory>
#include <optional>
#include <tuple>

#include <amulet/core/block_entity/block_entity.hpp>
#include <amulet/core/dll.hpp>
#include <amulet/core/version/version.hpp>

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
    template <typename VersionRangeT>
    BlockEntityComponentData(
        VersionRangeT&& version_range,
        std::uint16_t x_size,
        std::uint16_t z_size)
        : VersionRangeContainer(std::forward<VersionRangeT>(version_range))
        , _x_size(x_size)
        , _z_size(z_size)
        , _block_entities()
    {
    }

    AMULET_CORE_EXPORT void serialise(BinaryWriter&) const;
    AMULET_CORE_EXPORT static BlockEntityComponentData deserialise(BinaryReader&);

    std::uint16_t get_x_size() const { return _x_size; }
    std::uint16_t get_z_size() const { return _z_size; }

    const std::map<BlockEntityChunkCoord, std::shared_ptr<BlockEntity>>&
    get_block_entities() const
    {
        return _block_entities;
    }

    size_t get_size() const { return _block_entities.size(); }

    bool contains(
        const BlockEntityChunkCoord& coord) const
    {
        return _block_entities.contains(coord);
    }

    std::shared_ptr<BlockEntity> get(
        const BlockEntityChunkCoord& coord) const
    {
        return _block_entities.at(coord);
    }

    template <typename BlockEntityT>
    void set(
        const BlockEntityChunkCoord& coord,
        BlockEntityT&& block_entity)
    {
        std::shared_ptr<BlockEntity> block_entity_ptr;
        if constexpr (std::is_same_v<std::shared_ptr<BlockEntity>, std::decay_t<BlockEntityT>>) {
            block_entity_ptr = std::forward<BlockEntityT>(block_entity);
        } else {
            block_entity_ptr = std::make_shared<BlockEntity>(block_entity);
        }

        if (
            std::get<0>(coord) < 0 || std::get<2>(coord) < 0 || _x_size <= std::get<0>(coord) || _z_size <= std::get<2>(coord)) {
            throw std::invalid_argument(
                "Coord must be 0 <= " + std::to_string(std::get<0>(coord)) + " < " + std::to_string(_x_size) + "and 0 <= " + std::to_string(std::get<1>(coord)) + " < " + std::to_string(_z_size));
        }
        if (!(
                get_version_range().contains(
                    block_entity->get_platform(),
                    block_entity->get_version()))) {
            throw std::invalid_argument(
                "BlockEntity is incompatible with VersionRange.");
        }
        _block_entities.insert_or_assign(coord, std::move(block_entity));
    }

    void del(const BlockEntityChunkCoord& coord)
    {
        _block_entities.erase(coord);
    }
};

class BlockEntityComponent {
private:
    std::optional<std::shared_ptr<BlockEntityComponentData>> _value;

protected:
    // Null constructor
    BlockEntityComponent() = default;
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
