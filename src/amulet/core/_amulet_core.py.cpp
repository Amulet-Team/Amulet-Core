#include <pybind11/pybind11.h>

#include <amulet/pybind11_extensions/compatibility.hpp>

namespace py = pybind11;
namespace pyext = Amulet::pybind11_extensions;

void init_version(py::module);
void init_selection(py::module);
void init_block(py::module);
void init_block_entity(py::module);
void init_entity(py::module);
void init_biome(py::module);
void init_palette(py::module);
void init_chunk(py::module);

void init_module(py::module m)
{
    pyext::init_compiler_config(m);
    pyext::check_compatibility(py::module::import("amulet.zlib"), m);
    pyext::check_compatibility(py::module::import("amulet.nbt"), m);

    // Submodules
    init_version(m);
    init_selection(m);
    init_block(m);
    init_block_entity(m);
    init_entity(m);
    init_biome(m);
    init_palette(m);
    init_chunk(m);
}

PYBIND11_MODULE(_amulet_core, m)
{
    py::options options;
    options.disable_function_signatures();
    m.def("init", &init_module, py::doc("init(arg0: types.ModuleType) -> None"));
    options.enable_function_signatures();
}
