#include <amulet/dll.hpp>
#include <amulet/chunk_components/block_component.hpp>

namespace Amulet {
	AMULET_CORE_DLLX void BlockComponentData::serialise(BinaryWriter& writer) const {
		writer.writeNumeric<std::uint8_t>(1);
		get_palette()->serialise(writer);
		get_sections()->serialise(writer);
	}
	AMULET_CORE_DLLX std::shared_ptr<BlockComponentData> BlockComponentData::deserialise(BinaryReader& reader) {
		auto version = reader.readNumeric<std::uint8_t>();
		switch (version) {
		case 1:
		{
			auto palette = BlockPalette::deserialise(reader);
			auto sections = SectionArrayMap::deserialise(reader);
			return std::make_shared<BlockComponentData>(palette, sections);
		}
		default:
			throw std::invalid_argument("Unsupported BlockComponentData version " + std::to_string(version));
		}
	}

	AMULET_CORE_DLLX const std::string BlockComponent::ComponentID = "Amulet::BlockComponent";

	AMULET_CORE_DLLX std::optional<std::string> BlockComponent::serialise() const {
		if (_value) {
			return Amulet::serialise(**_value);
		}
		else {
			return std::nullopt;
		}
	}
	AMULET_CORE_DLLX void BlockComponent::deserialise(std::optional<std::string> data) {
		if (data) {
			_value = Amulet::deserialise<BlockComponentData>(*data);
		}
		else {
			_value = std::nullopt;
		}
	}
}
