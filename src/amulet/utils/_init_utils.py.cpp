#include <pybind11/pybind11.h>
#include <amulet/pybind11/py_module.hpp>
namespace py = pybind11;

void init_utils_numpy(py::module);

void init_utils(py::module m_parent){
    auto m = py::def_subpackage(m_parent, "utils");

    init_utils_numpy(m);
}
