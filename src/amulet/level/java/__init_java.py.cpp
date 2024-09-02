#include <string>
#include <vector>
#include <pybind11/pybind11.h>
#include <amulet/pybind11/py_module.hpp>
namespace py = pybind11;

void init_java_chunk_components(py::module);
void init_java_chunk(py::module);

void init_java(py::module m_parent) {
    auto m = m_parent.def_submodule("java");
    py::def_deferred(
        m,
        {
            py::getattr_path(m_parent, m, "level")//,
            //py::getattr_import("amulet.level.java._level", "JavaLevel")
        }
    );

    auto chunk_components_module = m.def_submodule("chunk_components");
    init_java_chunk_components(chunk_components_module);

    auto chunk_module = m.def_submodule("chunk");
    init_java_chunk(chunk_module);

}
