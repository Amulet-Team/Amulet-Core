#include <string>
#include <pybind11/pybind11.h>
#include <amulet/pybind11/py_module.hpp>
namespace py = pybind11;

void init_java(py::module);

void init_level(py::module m_parent) {
    auto m = m_parent.def_submodule("level");

    //from ._load import register_level_class, unregister_level_class, get_level, NoValidLevel
    //from .temporary_level import TemporaryLevel

    py::def_deferred(
        m,
        {
            py::getattr_path(m_parent, m, "level")//,
            //py::getattr_import("amulet.level.abc", "Level"),
            //py::getattr_import("amulet.level.java", "JavaLevel"),
            //py::getattr_import("amulet.level.bedrock", "BedrockLevel")
        }
    );

    // Submodules
    init_java(m);
}
