#include "biome_palette.hpp"

namespace Amulet {
void BiomePalette::serialise(BinaryWriter& writer) const
{
    writer.write_numeric<std::uint8_t>(1);
    get_version_range().serialise(writer);
    const auto& biomes = get_biomes();
    writer.write_numeric<std::uint64_t>(biomes.size());
    for (const auto& biome : biomes) {
        biome.serialise(writer);
    }
}
BiomePalette BiomePalette::deserialise(BinaryReader& reader)
{
    auto version = reader.read_numeric<std::uint8_t>();
    switch (version) {
    case 1: {
        auto version_range = VersionRange::deserialise(reader);
        auto count = reader.read_numeric<std::uint64_t>();
        BiomePalette palette(std::move(version_range));
        for (auto i = 0; i < count; i++) {
            if (palette.size() != palette.biome_to_index(Biome::deserialise(reader))) {
                throw std::runtime_error("Error deserialising BiomePalette");
            }
        }
        return palette;
    }
    default:
        throw std::invalid_argument("Unsupported BiomePalette version " + std::to_string(version));
    }
}
}
