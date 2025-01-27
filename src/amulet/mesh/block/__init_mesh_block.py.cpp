#include <pybind11/pybind11.h>

#include <pybind11_extensions/py_module.hpp>

namespace py = pybind11;

void init_block_mesh(py::module m_parent);

void init_mesh_block(py::module m_parent)
{
    auto m = pybind11_extensions::def_subpackage(m_parent, "block");
    init_block_mesh(m);
}
