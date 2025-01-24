#include <pybind11/pybind11.h>

#include <pybind11_extensions/py_module.hpp>

#include <amulet/utils/mutex.hpp>

namespace py = pybind11;

void init_test_mutex(py::module m_parent){
    auto m = pybind11_extensions::def_subpackage(m_parent, "test_mutex_");
    m.def("throw_deadlock", [](){ throw Amulet::Deadlock("Deadlock encountered."); });
}
