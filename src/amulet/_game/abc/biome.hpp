#pragma once

#include <pybind11/pybind11.h>

#include <amulet/biome.hpp>

namespace py = pybind11;

namespace Amulet {

class BiomeData {
private:
    py::object _biome_data;

public:
    BiomeData(py::object);

    Biome translate(const std::string& platform, const VersionNumber& version, const Biome& biome);
};

} // namespace Amulet
