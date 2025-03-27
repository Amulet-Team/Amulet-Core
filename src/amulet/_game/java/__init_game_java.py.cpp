#include <pybind11/pybind11.h>

#include <pybind11_extensions/py_module.hpp>

namespace py = pybind11;

void init_game_java_block(py::module);

void init_game_java(py::module m_parent)
{
    auto m = pybind11_extensions::def_subpackage(m_parent, "java");
    init_game_java_block(m);
}
