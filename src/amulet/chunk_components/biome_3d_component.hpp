#pragma once

#include <memory>
#include <tuple>
#include <optional>
#include <cstdint>
#include <memory>

#include <amulet/version.hpp>
#include <amulet/biome.hpp>
#include <amulet/palette/biome_palette.hpp>
#include <amulet/chunk_components/section_array_map.hpp>


namespace Amulet {
	class Biome3DComponentData {
	private:
		std::shared_ptr<BiomePalette> _palette;
		std::shared_ptr<SectionArrayMap> _sections;
	public:
		Biome3DComponentData(
			std::shared_ptr<VersionRange> version_range,
			const SectionShape& array_shape,
			std::shared_ptr<Biome> default_biome
		):
			_palette(std::make_shared<BiomePalette>(version_range)),
			_sections(std::make_shared<SectionArrayMap>(array_shape, static_cast<std::uint32_t>(0)))
		{
			_palette->biome_to_index(default_biome);
		}
		std::shared_ptr<BiomePalette> get_palette() {
			return _palette;
		}
		std::shared_ptr<SectionArrayMap> get_sections() {
			return _sections;
		}
	};

	class Biome3DComponent {
	private:
		std::optional<std::shared_ptr<Biome3DComponentData>> _value;
	protected:
		// Null constructor
		Biome3DComponent() {};
		// Default constructor
		void init(
			std::shared_ptr<VersionRange> version_range,
			const SectionShape& array_shape,
			std::shared_ptr<Biome> default_biome
		) { _value = std::make_shared<Biome3DComponentData>(version_range, array_shape, default_biome); }
		
		// Serialise the component data
		std::optional<std::string> serialise() const;
		// Deserialise the component
		void deserialise(std::optional<std::string>);
	public:
		static const std::string ComponentID;
		std::shared_ptr<Biome3DComponentData> get_biome() {
			if (_value) {
				return *_value;
			}
			throw std::runtime_error("BiomeComponent has not been loaded.");
		};
		void set_biome(std::shared_ptr<Biome3DComponentData> component) {
			if (_value) {
				if ((*_value)->get_sections()->get_array_shape() != component->get_sections()->get_array_shape()) {
					throw std::invalid_argument("New biome array shape does not match old array shape.");
				}
				if ((*_value)->get_palette()->get_version_range() != component->get_palette()->get_version_range()) {
					throw std::invalid_argument("New biome version range does not match old version range.");
				}
				_value = component;
			}
			else {
				throw std::runtime_error("BiomeComponent has not been loaded.");
			}
		};
	};
}
