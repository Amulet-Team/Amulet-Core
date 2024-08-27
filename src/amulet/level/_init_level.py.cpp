#include <string>
#include <pybind11/pybind11.h>
namespace py = pybind11;

void init_java(py::module);

void init_level(py::module level_module) {
    auto java_module = level_module.def_submodule("java");
    init_java(java_module);

    //from ._load import register_level_class, unregister_level_class, get_level, NoValidLevel
    //from .temporary_level import TemporaryLevel

    level_module.def(
        "__getattr__",
        [](py::object attr) -> py::object {
            if (py::isinstance<py::str>(attr)) {
                std::string name = attr.cast<std::string>();
                if (name == "Level") {
                    return py::module::import("amulet.level.abc").attr("Level");
                }
                else if (name == "JavaLevel") {
                    return py::module::import("amulet.level.java").attr("JavaLevel");
                }
                else if (name == "BedrockLevel") {
                    return py::module::import("amulet.level.bedrock").attr("BedrockLevel");
                }
                else {
                    throw py::attribute_error(name);
                }
            }
            else {
                throw py::attribute_error(py::repr(attr));
            }
        }
    );

    py::list all;
    all.append(py::str("Level"));
    all.append(py::str("java"));
    all.append(py::str("JavaLevel"));
    all.append(py::str("BedrockLevel"));
    level_module.attr("__all__") = all;
}
