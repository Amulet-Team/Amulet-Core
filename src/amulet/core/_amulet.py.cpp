#include <pybind11/pybind11.h>

#include <pybind11_extensions/compatibility.hpp>
#include <pybind11_extensions/py_module.hpp>

namespace py = pybind11;

void init_version();
void init_selection();
void init_block();
void init_block_entity();
void init_entity();
void init_biome();
void init_palette();
void init_chunk();
void init_chunk_components();

void init_module(py::module m)
{
    auto amulet_nbt = py::module::import("amulet.nbt");

    pybind11_extensions::init_compiler_config(m);
    pybind11_extensions::check_compatibility(amulet_nbt, m);

    // Submodules
    init_version();
    init_selection();
    init_block();
    init_block_entity();
    init_entity();
    init_biome();
    init_palette();
    init_chunk();
    init_chunk_components();
}

PYBIND11_MODULE(_amulet, m)
{
    py::options options;
    options.disable_function_signatures();
    m.def("init", &init_module, py::doc("init(arg0: types.ModuleType) -> None"));
    options.enable_function_signatures();
}
