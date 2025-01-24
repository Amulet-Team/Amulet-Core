#include <stdexcept>
#include <string>

#include <pybind11/pybind11.h>
#include <pybind11_extensions/compatibility.hpp>
#include <pybind11_extensions/py_module.hpp>
namespace py = pybind11;

void init_test_util(py::module);
void init_test_chunk(py::module);

void init_module(py::module m){
    auto amulet = py::module::import("amulet");

    pybind11_extensions::init_compiler_config(m);
    pybind11_extensions::check_compatibility(amulet, m);

    init_test_util(m);
    init_test_chunk(m);
}

PYBIND11_MODULE(_test_amulet, m) {
    py::options options;
    options.disable_function_signatures();
    m.def("init", &init_module, py::doc("init(arg0: types.ModuleType) -> None"));
    options.enable_function_signatures();
}
