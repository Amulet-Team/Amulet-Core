#include <stdexcept>
#include <string>

#include <pybind11/pybind11.h>
#include <pybind11_extensions/py_module.hpp>
namespace py = pybind11;

void init_test_mutex(py::module);

void init_module(py::module m){
}

PYBIND11_MODULE(_test_amulet, m) {
    py::options options;
    options.disable_function_signatures();
    m.def("init", &init_module, py::doc("init(arg0: types.ModuleType) -> None"));
    options.enable_function_signatures();
}
