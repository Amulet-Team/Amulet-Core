#include <string>
#include <vector>
#include <map>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <amulet/pybind11/py_module.hpp>
#include "java_chunk_decode.hpp"
#include "java_chunk_encode.hpp"
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

    auto m_chunk = m.def_submodule("_chunk");
    m_chunk.def(
        "decode_chunk",
        &Amulet::decode_java_chunk
    );
    m_chunk.def(
        "encode_chunk",
        &Amulet::encode_java_chunk
    );
}
