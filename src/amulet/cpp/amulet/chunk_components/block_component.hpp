#pragma once

#include <memory>
#include <tuple>
#include <optional>

#include <amulet/version.hpp>
#include <amulet/block.hpp>
#include <amulet/palette/block_palette.hpp>
#include <amulet/chunk_components/section_array_map.hpp>


namespace Amulet {
	class BlockComponentData {
	private:
		std::shared_ptr<BlockPalette> _palette;
		std::shared_ptr<SectionArrayMap> _sections;
	public:
		BlockComponentData(
			std::shared_ptr<VersionRange> version_range,
			const SectionShape& array_shape,
			std::shared_ptr<BlockStack> default_block
		):
			_palette(std::make_shared<BlockPalette>(version_range)),
			_sections(std::make_shared<SectionArrayMap>(array_shape, static_cast<std::uint32_t>(0)))
		{
			_palette->block_stack_to_index(default_block);
		}
		std::shared_ptr<BlockPalette> get_palette() {
			return _palette;
		}
		std::shared_ptr<SectionArrayMap> get_sections() {
			return _sections;
		}
	};

	class BlockComponent {
	private:
		std::optional<std::shared_ptr<BlockComponentData>> _value;
	protected:
		// Null constructor
		BlockComponent() {};
		// Default constructor
		void init(
			std::shared_ptr<VersionRange> version_range,
			const SectionShape& array_shape,
			std::shared_ptr<BlockStack> default_block
		) { _value = std::make_shared<BlockComponentData>(version_range, array_shape, default_block); }
		
		// Serialise the component data
		std::optional<std::string> serialise();
		// Deserialise the component
		void deserialise(std::optional<std::string>);
	public:
		static const std::string ComponentID;
		std::shared_ptr<BlockComponentData> get_block() {
			if (_value) {
				return *_value;
			}
			throw std::runtime_error("BlockComponent has not been loaded.");
		};
		void set_block(std::shared_ptr<BlockComponentData> component) {
			if (_value) {
				if ((*_value)->get_sections()->get_array_shape() != component->get_sections()->get_array_shape()) {
					throw std::invalid_argument("New array shape does not match old array shape.");
				}
				if ((*_value)->get_palette()->get_version_range() != component->get_palette()->get_version_range()) {
					throw std::invalid_argument("New version range does not match old version range.");
				}
				_value = component;
			}
			else {
				throw std::runtime_error("BlockComponent has not been loaded.");
			}
		};
	};
}