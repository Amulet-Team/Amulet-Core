#include <pybind11/pybind11.h>

#include <pybind11_extensions/py_module.hpp>

#include <amulet/utils/mutex.hpp>

namespace py = pybind11;

void init_test_lock(py::module m_parent){
    auto m = m_parent.def_submodule("test_lock_");
    m.def("throw_deadlock", [](){ throw Amulet::Deadlock("Deadlock encountered."); });
}
