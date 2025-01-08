#include <pybind11/pybind11.h>
namespace py = pybind11;

void init_block_palette(py::module);
void init_biome_palette(py::module);

void init_palette(py::module m_parent){
    auto m = m_parent.def_submodule("palette");

    auto block_palette_module = m.def_submodule("block_palette");
    init_block_palette(block_palette_module);

    auto biome_palette_module = m.def_submodule("biome_palette");
    init_biome_palette(biome_palette_module);

    m.attr("BlockPalette") = block_palette_module.attr("BlockPalette");
    m.attr("BiomePalette") = biome_palette_module.attr("BiomePalette");
}
