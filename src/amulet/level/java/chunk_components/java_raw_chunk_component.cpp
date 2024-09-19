#include <optional>
#include <stdexcept>

#include <amulet/io/binary_writer.hpp>
#include <amulet/io/binary_reader.hpp>

#include <amulet_nbt/nbt_encoding/binary.hpp>

#include <amulet/level/java/chunk_components/java_raw_chunk_component.hpp>

namespace Amulet {
	const std::string JavaRawChunkComponent::ComponentID = "Amulet::JavaRawChunkComponent";

	std::optional<std::string> JavaRawChunkComponent::serialise() const {
		if (_raw_data) {
			BinaryWriter writer;
			writer.writeNumeric<std::uint8_t>(1);
			const auto& raw_data = _raw_data.value();
			writer.writeNumeric<std::uint64_t>(raw_data->size());
			for (const auto& [k, v] : *raw_data) {
				writer.writeSizeAndBytes(k);
				AmuletNBT::write_nbt(writer, *v);
			}
			return writer.getBuffer();
		}
		else {
			return std::nullopt;
		}
	}
	void JavaRawChunkComponent::deserialise(std::optional<std::string> data) {
		if (data) {
			size_t position = 0;
			BinaryReader reader(data.value(), position);
			auto version = reader.readNumeric<std::uint8_t>();
			switch (version) {
				case 1:
					{
						auto raw_data = std::make_shared<Amulet::JavaRawChunkType>();
						auto count = reader.readNumeric<std::uint64_t>();
						for (auto i = 0; i < count; i++) {
							auto key = reader.readSizeAndBytes();
							auto tag = std::make_shared<AmuletNBT::NamedTag>(AmuletNBT::read_nbt(reader));
							raw_data->emplace(key, tag);
						}
						_raw_data = raw_data;
					}
					break;
				default:
					throw std::invalid_argument("Unsupported JavaRawChunkComponent version " + std::to_string(version));
			}
		}
		else {
			_raw_data = std::nullopt;
		}
	}
}
