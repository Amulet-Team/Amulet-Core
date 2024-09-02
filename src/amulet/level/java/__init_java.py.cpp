#include <string>
#include <vector>
#include <pybind11/pybind11.h>
namespace py = pybind11;

void init_java_chunk_components(py::module);
void init_java_chunk(py::module);

void init_java(py::module m_parent) {
    auto m = m_parent.def_submodule("java");
    init_java_chunk_components(chunk_components_module);

    auto chunk_module = m.def_submodule("chunk");
    init_java_chunk(chunk_module);

    java_module.def(
        "__getattr__",
        [](py::object attr) -> py::object {
            if (py::isinstance<py::str>(attr)) {
                std::string name = attr.cast<std::string>();
                if (name == "JavaLevel") {
                    return py::module::import("amulet.level.java._level").attr("JavaLevel");
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
    all.append(py::str("chunk_components"));
    all.append(py::str("JavaLevel"));
    java_module.attr("__all__") = all;
}
