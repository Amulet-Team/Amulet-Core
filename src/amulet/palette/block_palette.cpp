#include "block_palette.hpp"

namespace Amulet {
	void BlockPalette::serialise(BinaryWriter& writer) const {
		writer.writeNumeric<std::uint8_t>(1);
		get_version_range()->serialise(writer);
		const auto& blocks = get_blocks();
		writer.writeNumeric<std::uint64_t>(blocks.size());
		for (const auto& block : blocks) {
			block->serialise(writer);
		}
	}
	std::shared_ptr<BlockPalette> BlockPalette::deserialise(BinaryReader& reader) {
		auto version = reader.readNumeric<std::uint8_t>();
		switch (version) {
		case 1:
		{
			auto version_range = VersionRange::deserialise(reader);
			auto count = reader.readNumeric<std::uint64_t>();
			auto palette = std::make_shared<BlockPalette>(version_range);
			for (auto i = 0; i < count; i++) {
				if (palette->size() != palette->block_stack_to_index(BlockStack::deserialise(reader))) {
					throw std::runtime_error("Error deserialising BlockPalette");
				}
			}
			return palette;
		}
		default:
			throw std::invalid_argument("Unsupported BlockComponentData version " + std::to_string(version));
		}
	}
}
