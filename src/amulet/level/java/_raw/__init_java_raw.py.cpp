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
    auto m = py::def_subpackage(m_parent, "_raw");

    auto m_chunk = m.def_submodule("_chunk");
    m_chunk.def(
        "decode_chunk",
        &Amulet::decode_java_chunk
    );
    m_chunk.def(
        "encode_chunk",
        &Amulet::encode_java_chunk
    );

    m.attr("JavaRawLevel") = py::module::import("amulet.level.java._raw._level").attr("JavaRawLevel");
    m.attr("JavaCreateArgsV1") = py::module::import("amulet.level.java._raw._level").attr("JavaCreateArgsV1");
    m.attr("JavaRawDimension") = py::module::import("amulet.level.java._raw._dimension").attr("JavaRawDimension");
    m.attr("InternalDimensionId") = py::module::import("amulet.level.java._raw._typing").attr("InternalDimensionId");
}
