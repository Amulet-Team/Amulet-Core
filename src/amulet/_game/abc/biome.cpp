#include "biome.hpp"

namespace Amulet {

BiomeData::BiomeData(py::object biome_data)
    : _biome_data(std::make_unique<py::object>(biome_data))
{
}

BiomeData::~BiomeData()
{
    py::gil_scoped_acquire gil;
    _biome_data = nullptr;
}

Biome BiomeData::translate(const std::string& platform, const VersionNumber& version, const Biome& biome)
{
    py::gil_scoped_acquire gil;
    return _biome_data->attr("translate")(platform, py::cast(version), py::cast(biome)).cast<Biome>();
}

} // namespace Amulet
