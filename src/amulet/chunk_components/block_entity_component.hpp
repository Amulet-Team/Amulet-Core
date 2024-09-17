#pragma once

#include <memory>
#include <tuple>
#include <optional>
#include <cstdint>
#include <memory>
#include <map>

#include <amulet/version.hpp>
#include <amulet/block_entity.hpp>


namespace Amulet {
	typedef std::tuple<std::uint16_t, std::int64_t, std::uint16_t> BlockEntityChunkCoord;
	class BlockEntityComponentData: public VersionRangeContainer {
	private:
		std::uint16_t _x_size;
		std::uint16_t _z_size;
		std::map<
			BlockEntityChunkCoord,
			std::shared_ptr<BlockEntity>
		> _block_entities;
	public:
		BlockEntityComponentData(
			std::shared_ptr<VersionRange> version_range,
			const std::uint16_t& x_size,
			const std::uint16_t& z_size
		) :
			VersionRangeContainer(version_range),
			_x_size(x_size),
			_z_size(z_size),
			_block_entities()
		{}

		std::uint16_t get_x_size() const { return _x_size; }
		std::uint16_t get_z_size() const { return _z_size; }

		const std::map<
			BlockEntityChunkCoord,
			std::shared_ptr<BlockEntity>
		>& get_block_entities() const {
			return _block_entities;
		}

		size_t get_size() const { return _block_entities.size(); }
		
		bool contains(
			const BlockEntityChunkCoord& coord
		) const {
			return _block_entities.contains(coord);
		}

		std::shared_ptr<BlockEntity> get(
			const BlockEntityChunkCoord& coord
		) const {
			return _block_entities.at(coord);
		}

		void set(
			const BlockEntityChunkCoord& coord,
			std::shared_ptr<BlockEntity> block_entity
		) {
			if (
				std::get<0>(coord) < 0 ||
				std::get<2>(coord) < 0 ||
				_x_size <= std::get<0>(coord) ||
				_z_size <= std::get<2>(coord)
			){
				throw std::invalid_argument(
					"Coord must be 0 <= " +
					std::to_string(std::get<0>(coord)) +
					" < " +
					std::to_string(_x_size) +
					"and 0 <= " +
					std::to_string(std::get<1>(coord)) +
					" < " +
					std::to_string(_z_size)
				);
			}
			if (!(
				get_version_range()->contains(
					block_entity->get_platform(), 
					*block_entity->get_version()
				)
			)){
				throw std::invalid_argument(
					"BlockEntity is incompatible with VersionRange."
				);
			}
			_block_entities[coord] = block_entity;
		}

		void del(
			const BlockEntityChunkCoord& coord
		) {
			_block_entities.erase(coord);
		}

	};

	class BlockEntityComponent {
	private:
		std::optional<std::shared_ptr<BlockEntityComponentData>> _value;
	protected:
		// Null constructor
		BlockEntityComponent() {};
		// Default constructor
		void init(
			std::shared_ptr<VersionRange> version_range,
			const std::uint16_t& x_size,
			const std::uint16_t& z_size
		) {
			_value = std::make_shared<BlockEntityComponentData>(version_range, x_size, z_size);
		}

		// Serialise the component data
		std::optional<std::string> serialise() const;
		// Deserialise the component
		void deserialise(std::optional<std::string>);
	public:
		static const std::string ComponentID;
		std::shared_ptr<BlockEntityComponentData> get_block_entity() {
			if (_value) {
				return *_value;
			}
			throw std::runtime_error("BlockEntityComponent has not been loaded.");
		};
		void set_block_entity(std::shared_ptr<BlockEntityComponentData> component) {
			if (_value) {
				if (
					(*_value)->get_x_size() != component->get_x_size() ||
					(*_value)->get_z_size() != component->get_z_size()
				) {
					throw std::invalid_argument("New BlockEntityComponent shape does not match old shape.");
				}
				if ((*_value)->get_version_range() != component->get_version_range()) {
					throw std::invalid_argument("New BlockEntityComponent version range does not match old version range.");
				}
				_value = component;
			}
			else {
				throw std::runtime_error("BlockEntityComponent has not been loaded.");
			}
		};
	};
}
