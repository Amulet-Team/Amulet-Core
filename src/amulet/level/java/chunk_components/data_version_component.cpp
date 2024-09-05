#include <cstdint>
#include <optional>

#include <amulet/io/binary_writer.hpp>
#include <amulet/io/binary_reader.hpp>

#include <amulet/level/java/chunk_components/data_version_component.hpp>

namespace Amulet {
	const std::string DataVersionComponent::ComponentID = "Amulet::DataVersionComponent";

	std::optional<std::string> DataVersionComponent::serialise() const {
		if (_data_version) {
			BinaryWriter writer;
			writer.writeNumeric<std::int64_t>(_data_version.value());
			return writer.getBuffer();
		}
		else {
			return std::nullopt;
		}
	}
	void DataVersionComponent::deserialise(std::optional<std::string> data) {
		if (data) {
			size_t position = 0;
			BinaryReader reader(data.value(), position);
			_data_version = reader.readNumeric<std::int64_t>();
		}
		else {
			_data_version = std::nullopt;
		}
	}
}
