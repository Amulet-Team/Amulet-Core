#include "block_palette.hpp"

namespace Amulet {
void BlockPalette::serialise(BinaryWriter& writer) const
{
    writer.write_numeric<std::uint8_t>(1);
    get_version_range().serialise(writer);
    const auto& blocks = get_blocks();
    writer.write_numeric<std::uint64_t>(blocks.size());
    for (const auto& block : blocks) {
        block.serialise(writer);
    }
}
BlockPalette BlockPalette::deserialise(BinaryReader& reader)
{
    auto version = reader.read_numeric<std::uint8_t>();
    switch (version) {
    case 1: {
        auto version_range = VersionRange::deserialise(reader);
        auto count = reader.read_numeric<std::uint64_t>();
        BlockPalette palette(std::move(version_range));
        for (auto i = 0; i < count; i++) {
            if (palette.size() != palette.block_stack_to_index(BlockStack::deserialise(reader))) {
                throw std::runtime_error("Error deserialising BlockPalette");
            }
        }
        return palette;
    }
    default:
        throw std::invalid_argument("Unsupported BlockPalette version " + std::to_string(version));
    }
}
}
