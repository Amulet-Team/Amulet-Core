#pragma once

#include <pybind11/pybind11.h>

#include "biome.hpp"
#include "block.hpp"

namespace py = pybind11;

namespace Amulet {

class GameVersion{
protected:
    py::object _game_version;

public:
    GameVersion(py::object);

    std::shared_ptr<BiomeData> get_biome_data();
    std::shared_ptr<BlockData> get_block_data();
};

} // namespace Amulet
