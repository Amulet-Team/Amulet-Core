#include <pybind11/pybind11.h>
#include <pybind11_extensions/py_module.hpp>
namespace py = pybind11;

py::module init_level_loader(py::module);
py::module init_level_abc(py::module);
py::module init_java(py::module);

void init_level(py::module m_parent)
{
    auto m = pybind11_extensions::def_subpackage(m_parent, "level");

    init_level_abc(m);
    m.attr("Level") = py::module::import("amulet.level.abc").attr("Level");

    init_level_loader(m);
    m.attr("get_level") = py::module::import("amulet.level.loader").attr("get_level");
    m.attr("NoValidLevelLoader") = py::module::import("amulet.level.loader").attr("NoValidLevelLoader");

    // from .temporary_level import TemporaryLevel

    // Submodules
    // auto java_module = init_java(m);
    // m.attr("JavaLevel") = java_module.attr("JavaLevel");

    // m.attr("BedrockLevel") = py::module::import("amulet.level.bedrock").attr("BedrockLevel");
}
