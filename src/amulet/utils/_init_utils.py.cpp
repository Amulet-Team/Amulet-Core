#include <pybind11/pybind11.h>
namespace py = pybind11;

void init_utils_numpy(py::module);

void init_utils(py::module m_parent){
    auto m = m_parent.def_submodule("utils");

    init_utils_numpy(m);
}
