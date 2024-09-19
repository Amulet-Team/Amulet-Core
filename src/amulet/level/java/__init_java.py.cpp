#include <string>
#include <vector>
#include <pybind11/pybind11.h>
#include <amulet/pybind11/py_module.hpp>
namespace py = pybind11;

void init_long_array(py::module);
void init_java_chunk_components(py::module);
void init_java_chunk(py::module);
void init_java_raw(py::module);

void init_java(py::module m_parent) {
    auto m = m_parent.def_submodule("java");
    py::def_deferred(
        m,
        {
            py::deferred_package_path(m_parent, m, "java"),
            py::deferred_import("amulet.level.java._level", "JavaLevel")
        }
    );

    init_long_array(m);
    init_java_chunk_components(m);
    init_java_chunk(m);
    init_java_raw(m);
}
