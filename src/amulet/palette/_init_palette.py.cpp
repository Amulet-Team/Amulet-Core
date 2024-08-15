#include <pybind11/pybind11.h>
namespace py = pybind11;

void init_block_palette(py::module);
void init_biome_palette(py::module);

void init_palette(py::module palette_module){
    auto block_palette_module = palette_module.def_submodule("block_palette");
    init_block_palette(block_palette_module);

    auto biome_palette_module = palette_module.def_submodule("biome_palette");
    init_biome_palette(biome_palette_module);

    palette_module.attr("BlockPalette") = block_palette_module.attr("BlockPalette");
    palette_module.attr("BiomePalette") = biome_palette_module.attr("BiomePalette");
}
