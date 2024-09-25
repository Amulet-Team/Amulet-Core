#include <string>
#include <pybind11/pybind11.h>
#include <amulet/pybind11/py_module.hpp>
namespace py = pybind11;

py::module init_java(py::module);

void init_level(py::module m_parent) {
    auto m = py::def_subpackage(m_parent, "level");

    m.attr("Level") = py::module::import("amulet.level.abc").attr("Level");

    m.attr("register_level_class") = py::module::import("amulet.level._load").attr("register_level_class");
    m.attr("unregister_level_class") = py::module::import("amulet.level._load").attr("unregister_level_class");
    m.attr("get_level") = py::module::import("amulet.level._load").attr("get_level");
    m.attr("NoValidLevel") = py::module::import("amulet.level._load").attr("NoValidLevel");

    //from .temporary_level import TemporaryLevel

    // Submodules
    auto java_module = init_java(m);
    m.attr("JavaLevel") = java_module.attr("JavaLevel");
    
    //m.attr("BedrockLevel") = py::module::import("amulet.level.bedrock").attr("BedrockLevel");
}
