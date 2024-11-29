#include <stdexcept>
#include <string>

#include <pybind11/pybind11.h>
#include <pybind11_extensions/py_module.hpp>
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
void init_block_mesh(py::module);





void init_module(py::module m){
    auto amulet_nbt = py::module::import("amulet_nbt");
    auto leveldb = py::module::import("leveldb");

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
    init_block_mesh(m);
}

PYBIND11_MODULE(_amulet, m) {
    m.def("init", &init_module);
}
