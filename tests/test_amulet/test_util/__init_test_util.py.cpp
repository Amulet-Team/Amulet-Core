#include <pybind11/pybind11.h>
#include <pybind11_extensions/py_module.hpp>
namespace py = pybind11;

void init_test_mutex(py::module);
void init_test_task_manager(py::module);

void init_test_util(py::module m_parent){
    auto test_util = pybind11_extensions::def_subpackage(m_parent, "test_util");
    init_test_task_manager(test_util);
    init_test_mutex(test_util);
}
