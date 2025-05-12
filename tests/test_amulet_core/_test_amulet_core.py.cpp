#include <pybind11/pybind11.h>

#include <amulet/pybind11_extensions/compatibility.hpp>
#include <amulet/pybind11_extensions/py_module.hpp>

#include <stdexcept>
#include <string>

namespace py = pybind11;
namespace pyext = Amulet::pybind11_extensions;

void init_test_chunk(py::module);

void init_module(py::module m){
    pyext::init_compiler_config(m);
    pyext::check_compatibility(py::module::import("amulet.core"), m);

    init_test_chunk(m);
}

PYBIND11_MODULE(_test_amulet_core, m) {
    py::options options;
    options.disable_function_signatures();
    m.def("init", &init_module, py::doc("init(arg0: types.ModuleType) -> None"));
    options.enable_function_signatures();
}
