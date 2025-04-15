#pragma once

#include <pybind11/pybind11.h>

#include <memory>

#include <amulet/biome.hpp>

namespace py = pybind11;

namespace Amulet {

class BiomeData {
private:
    std::unique_ptr<py::object> _biome_data;

public:
    BiomeData(py::object);
    ~BiomeData();

    Biome translate(const std::string& platform, const VersionNumber& version, const Biome& biome);
};

} // namespace Amulet
