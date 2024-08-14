#include <pybind11/pybind11.h>
namespace py = pybind11;

void init_utils(py::module);
void init_version(py::module);
void init_block(py::module);
void init_biome(py::module);
void init_palette(py::module);
void init_chunk(py::module);

static bool init_run = false;

void init_amulet(py::module amulet){
    if (init_run){
        return;
    }
    init_run = true;
    auto utils_module = amulet.def_submodule("utils");
    init_utils(utils_module);

    auto version_module = amulet.def_submodule("version");
    init_version(version_module);

    auto block_module = amulet.def_submodule("block");
    init_block(block_module);

    auto biome_module = amulet.def_submodule("biome");
    init_biome(biome_module);

    auto palette_module = amulet.def_submodule("palette");
    init_palette(palette_module);

    auto chunk_module = amulet.def_submodule("chunk");
    init_chunk(chunk_module);
}

PYBIND11_MODULE(__init__, m) { init_amulet(m); }
PYBIND11_MODULE(amulet, m) { init_amulet(m); }
