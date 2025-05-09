#include <pybind11/pybind11.h>

#include <amulet/pybind11_extensions/py_module.hpp>

namespace py = pybind11;
namespace pyext = Amulet::pybind11_extensions;

void init_block_palette(py::module);
void init_biome_palette(py::module);

void init_palette(py::module m_parent)
{
    auto m = pyext::def_subpackage(m_parent, "palette");

    auto block_palette_module = m.def_submodule("block_palette");
    init_block_palette(block_palette_module);

    auto biome_palette_module = m.def_submodule("biome_palette");
    init_biome_palette(biome_palette_module);

    m.attr("BlockPalette") = block_palette_module.attr("BlockPalette");
    m.attr("BiomePalette") = biome_palette_module.attr("BiomePalette");
}
