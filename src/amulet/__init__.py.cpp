#include <pybind11/pybind11.h>
namespace py = pybind11;

void init_collections(py::module);
void init_utils(py::module);
void init_version(py::module);
void init_block(py::module);
void init_block_entity(py::module);
void init_biome(py::module);
void init_palette(py::module);
void init_chunk(py::module);
void init_chunk_components(py::module);
void init_level(py::module);

static bool init_run = false;

void init_amulet(py::module m){
    if (init_run){ return; }
    init_run = true;

    // This is normally added after initilsation but we need it to pass to subpackages.
    // This may cause issues with frozen installs.
    m.attr("__path__") = py::module::import("importlib.util").attr("find_spec")("amulet").attr("submodule_search_locations");

    py::module::import("amulet_nbt");

    py::module::import("amulet._init").attr("init")(m);

    // Submodules
    init_collections(m);
    init_utils(m);
    init_version(m);
    init_block(m);
    init_block_entity(m);
    init_biome(m);
    init_palette(m);
    init_chunk(m);
    init_chunk_components(m);
    init_level(m);
}

PYBIND11_MODULE(__init__, m) { init_amulet(m); }
PYBIND11_MODULE(amulet, m) { init_amulet(m); }
