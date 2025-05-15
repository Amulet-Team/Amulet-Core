#include <pybind11/pybind11.h>

#include <amulet/pybind11_extensions/compatibility.hpp>

namespace py = pybind11;
namespace pyext = Amulet::pybind11_extensions;

void init_test_biome(py::module);
void init_test_block(py::module);
void init_test_block_entity(py::module);
void init_test_chunk(py::module);
void init_test_chunk_components(py::module);
void init_test_entity(py::module);
void init_test_palette(py::module);
void init_test_selection(py::module);
void init_test_version(py::module);

void init_module(py::module m){
    pyext::init_compiler_config(m);
    pyext::check_compatibility(py::module::import("amulet.core"), m);

    init_test_biome(m);
    init_test_block(m);
    init_test_block_entity(m);
    init_test_chunk(m);
    init_test_chunk_components(m);
    init_test_entity(m);
    init_test_palette(m);
    init_test_selection(m);
    init_test_version(m);
}

PYBIND11_MODULE(_test_amulet_core, m) {
    py::options options;
    options.disable_function_signatures();
    m.def("init", &init_module, py::doc("init(arg0: types.ModuleType) -> None"));
    options.enable_function_signatures();
}
