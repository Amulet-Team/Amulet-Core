#include <pybind11/pybind11.h>
#include <amulet/pybind11/py_module.hpp>
namespace py = pybind11;

void init_utils_numpy(py::module);

void init_utils(py::module m_parent){
    auto m = m_parent.def_submodule("utils");

    init_utils_numpy(m);

    py::def_deferred(
        m,
        {
            py::deferred_package_path(m_parent, m, "utils")
        }
    );
}
