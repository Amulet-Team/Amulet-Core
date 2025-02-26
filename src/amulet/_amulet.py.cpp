#include <pybind11/pybind11.h>

#include <stdexcept>
#include <string>

#include <pybind11_extensions/compatibility.hpp>
#include <pybind11_extensions/py_module.hpp>

namespace py = pybind11;

void init_collections(py::module);
void init_utils(py::module);
void init_version(py::module);
void init_selection(py::module);
void init_block(py::module);
void init_block_entity(py::module);
void init_entity(py::module);
void init_biome(py::module);
void init_palette(py::module);
void init_chunk(py::module);
void init_chunk_components(py::module);
void init_level(py::module);
void init_mesh(py::module);
void init_image(py::module);

void init_module(py::module m)
{
    auto amulet_nbt = py::module::import("amulet_nbt");
    auto leveldb = py::module::import("leveldb");

    pybind11_extensions::init_compiler_config(m);
    pybind11_extensions::check_compatibility(amulet_nbt, m);
    pybind11_extensions::check_compatibility(leveldb, m);

    // Submodules
    init_collections(m);
    init_utils(m);
    init_version(m);
    init_selection(m);
    init_block(m);
    init_block_entity(m);
    init_entity(m);
    init_biome(m);
    init_palette(m);
    init_chunk(m);
    init_chunk_components(m);
    init_level(m);
    init_mesh(m);
    init_image(m);
}

PYBIND11_MODULE(_amulet, m)
{
    py::options options;
    options.disable_function_signatures();
    m.def("init", &init_module, py::doc("init(arg0: types.ModuleType) -> None"));
    options.enable_function_signatures();
}
