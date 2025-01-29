#include <pybind11/pybind11.h>

#include <string>
#include <vector>

#include <pybind11_extensions/py_module.hpp>

namespace py = pybind11;

void init_long_array(py::module);
void init_java_chunk_components(py::module);
void init_java_chunk(py::module);
void init_java_anvil(py::module);
void init_java_raw(py::module);

py::module init_java(py::module m_parent)
{
    auto m = pybind11_extensions::def_subpackage(m_parent, "java");

    init_long_array(m);
    init_java_chunk_components(m);
    init_java_chunk(m);
    init_java_anvil(m);

    //    m.attr("JavaRawLevel") = py::module::import("amulet.level.java.raw._level").attr("JavaRawLevel");
    //    m.attr("JavaCreateArgsV1") = py::module::import("amulet.level.java.raw._level").attr("JavaCreateArgsV1");
    //    m.attr("JavaRawDimension") = py::module::import("amulet.level.java.raw._dimension").attr("JavaRawDimension");
    //    m.attr("JavaInternalDimensionID") = py::module::import("amulet.level.java.raw._typing").attr("JavaInternalDimensionID");
    //    m.attr("JavaLevel") = py::module::import("amulet.level.java._level").attr("JavaLevel");

    return m;
}
