#include <string>
#include <vector>
#include <map>
#include <pybind11/pybind11.h>
#include <amulet/pybind11/py_module.hpp>
namespace py = pybind11;

void init_java_chunk_decode(py::module);
void init_java_chunk_encode(py::module);

void init_java_raw(py::module m_parent) {
    auto m = m_parent.def_submodule("_raw");
    py::def_deferred(
        m,
        {
            py::deferred_package_path(m_parent, m, "_raw"),
            //py::deferred_import("amulet.level.java._raw._level", "JavaRawLevel"),
            //py::deferred_import("amulet.level.java._raw._level", "JavaCreateArgsV1"),
            //py::deferred_import("amulet.level.java._raw._dimension", "JavaRawDimension"),
            py::deferred_import("amulet.level.java._raw._typing", "InternalDimensionId")
        }
    );

    // Submodules
    init_java_chunk_decode(m);
    init_java_chunk_encode(m);
}
