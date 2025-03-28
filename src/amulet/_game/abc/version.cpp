#include "version.hpp"

namespace Amulet {

GameVersion::GameVersion(py::object game_version)
    : _game_version(game_version)
{
}

std::shared_ptr<BiomeData> GameVersion::get_biome_data()
{
    py::gil_scoped_acquire gil;
    return std::make_shared<BiomeData>(_game_version.attr("biome"));
}

std::shared_ptr<BlockData> GameVersion::get_block_data()
{
    py::gil_scoped_acquire gil;
    return std::make_shared<BlockData>(_game_version.attr("block"));
}

} // namespace Amulet
