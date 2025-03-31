#include "biome.hpp"

namespace Amulet {

BiomeData::BiomeData(py::object biome_data)
    : _biome_data(biome_data)
{
}

Biome BiomeData::translate(const std::string& platform, const VersionNumber& version, const Biome& biome)
{
    py::gil_scoped_acquire gil;
    return _biome_data.attr("translate")(platform, py::cast(version), py::cast(biome)).cast<Biome>();
}

} // namespace Amulet
