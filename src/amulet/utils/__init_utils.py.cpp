#include <pybind11/pybind11.h>

#include <pybind11_extensions/py_module.hpp>

namespace py = pybind11;

void init_utils_numpy(py::module);
void init_task_manager(py::module);
void init_lock(py::module);
void init_logging(py::module);
void init_signal(py::module);

void init_utils(py::module m_parent)
{
    auto m = pybind11_extensions::def_subpackage(m_parent, "utils");

    init_utils_numpy(m);
    init_signal(m);
    init_task_manager(m);
    init_lock(m);
    init_logging(m);
}
