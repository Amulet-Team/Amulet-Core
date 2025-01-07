#include <memory>

#include <pybind11/pybind11.h>
#include <pybind11_extensions/py_module.hpp>

#include "level.hpp"

namespace py = pybind11;

py::module init_level_abc_level(py::module m_parent)
{
    auto m = pybind11_extensions::def_subpackage(m_parent, "level");

    py::class_<Amulet::Level, std::shared_ptr<Amulet::Level>> Level(m, "Level");
    Level.def("is_open", &Amulet::Level::is_open);

    return m;
}
