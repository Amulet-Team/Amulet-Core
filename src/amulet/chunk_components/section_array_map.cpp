#include <string>

#include <amulet/io/binary_writer.hpp>
#include <amulet/io/binary_reader.hpp>

#include "section_array_map.hpp"

namespace Amulet {
	void IndexArray3D::serialise(BinaryWriter& writer) const {
		writer.writeNumeric<std::uint8_t>(1);
		
		// Write array shape
		const auto& array_shape = get_shape();
		writer.writeNumeric<std::uint16_t>(std::get<0>(array_shape));
		writer.writeNumeric<std::uint16_t>(std::get<1>(array_shape));
		writer.writeNumeric<std::uint16_t>(std::get<2>(array_shape));

		// Write array
		const auto& size = get_size();
		const auto* buffer = get_buffer();
		for (auto i = 0; i < size; i++) {
			writer.writeNumeric<std::uint32_t>(buffer[i]);
		}
	}
	std::shared_ptr<IndexArray3D> IndexArray3D::deserialise(BinaryReader& reader) {
		auto version = reader.readNumeric<std::uint8_t>();
		switch (version) {
		case 1:
		{
			// Read array shape
			auto array_shape = std::make_tuple(
				reader.readNumeric<std::uint16_t>(),
				reader.readNumeric<std::uint16_t>(),
				reader.readNumeric<std::uint16_t>()
			);

			// Construct instance
			auto self = std::make_shared<IndexArray3D>(array_shape);

			// Read array
			const auto& size = self->get_size();
			auto* buffer = self->get_buffer();
			for (auto i = 0; i < size; i++) {
				buffer[i] = reader.readNumeric<std::uint32_t>();
			}

			return self;
		}
		default:
			throw std::invalid_argument("Unsupported IndexArray3D version " + std::to_string(version));
		}
	}

	void SectionArrayMap::serialise(BinaryWriter& writer) const {
		writer.writeNumeric<std::uint8_t>(1);
		
		// Write array shape
		const auto& array_shape = get_array_shape();
		writer.writeNumeric<std::uint16_t>(std::get<0>(array_shape));
		writer.writeNumeric<std::uint16_t>(std::get<1>(array_shape));
		writer.writeNumeric<std::uint16_t>(std::get<2>(array_shape));
		
		// Write default array
		std::visit(
			[&writer](auto&& arg) {
				using T = std::decay_t<decltype(arg)>;
				if constexpr (std::is_same_v<T, std::uint32_t>) {
					writer.writeNumeric<std::uint8_t>(0);
					writer.writeNumeric<std::uint32_t>(arg);
				}
				else {
					writer.writeNumeric<std::uint8_t>(1);
					arg->serialise(writer);
				}
			}, 
			get_default_array()
		);

		// Write arrays
		const auto& arrays = get_arrays();
		writer.writeNumeric<std::uint64_t>(arrays.size());
		for (const auto& [cy, arr] : arrays) {
			writer.writeNumeric<std::int64_t>(cy);
			arr->serialise(writer);
		}
	}
	std::shared_ptr<SectionArrayMap> SectionArrayMap::deserialise(BinaryReader& reader) {
		auto version = reader.readNumeric<std::uint8_t>();
		switch (version) {
		case 1:
		{
			// Read array shape
			auto array_shape = std::make_tuple(
				reader.readNumeric<std::uint16_t>(),
				reader.readNumeric<std::uint16_t>(),
				reader.readNumeric<std::uint16_t>()
			);

			// Read default array
			auto default_array_state = reader.readNumeric<std::uint8_t>();
			std::variant<std::uint32_t, std::shared_ptr<IndexArray3D>> default_array;
			switch (default_array_state) {
			case 0:
				default_array = reader.readNumeric<std::uint32_t>();
				break;
			case 1:
				default_array = IndexArray3D::deserialise(reader);
				break;
			default:
				throw std::invalid_argument("Invalid default array state value " + std::to_string(default_array_state));
			}

			// Construct instance
			auto self = std::make_shared<SectionArrayMap>(array_shape, default_array);
			
			// Populate arrays
			auto array_count = reader.readNumeric<std::uint64_t>();
			for (auto i = 0; i < array_count; i++) {
				auto cy = reader.readNumeric<std::int64_t>();
				self->set_section(cy, IndexArray3D::deserialise(reader));
			}
			
			return self;
		}
		default:
			throw std::invalid_argument("Unsupported BlockComponentData version " + std::to_string(version));
		}
	}
}
