#include <pybind11/pybind11.h>

#include <pybind11_extensions/py_module.hpp>

namespace py = pybind11;

void init_test_anvil(py::module m_parent);

void init_test_java(py::module m_parent){
    auto m = pybind11_extensions::def_subpackage(m_parent, "test_java");
    init_test_anvil(m);
}
