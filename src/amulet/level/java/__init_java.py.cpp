#include <pybind11/pybind11.h>

#include <string>
#include <vector>

#include <pybind11_extensions/py_module.hpp>

namespace py = pybind11;

void init_long_array(py::module);
void init_java_chunk_components(py::module);
void init_java_chunk(py::module);
void init_java_anvil(py::module);
py::module init_java_raw_dimension(py::module);
py::module init_java_raw_level(py::module);
py::module init_java_chunk_handle(py::module);
py::module init_java_dimension(py::module);
py::module init_java_level(py::module);

py::module init_java(py::module m_parent)
{
    auto m = pybind11_extensions::def_subpackage(m_parent, "java");

    init_long_array(m);
    init_java_chunk_components(m);
    init_java_chunk(m);
    init_java_anvil(m);

    auto raw_dimension = init_java_raw_dimension(m);
    m.attr("JavaRawDimension") = raw_dimension.attr("JavaRawDimension");

    auto raw_level = init_java_raw_level(m);
    m.attr("JavaCreateArgsV1") = raw_level.attr("JavaCreateArgsV1");
    m.attr("JavaRawLevel") = raw_level.attr("JavaRawLevel");

    auto chunk_handle = init_java_chunk_handle(m);
    m.attr("JavaChunkHandle") = chunk_handle.attr("JavaChunkHandle");

    auto dimension = init_java_dimension(m);
    m.attr("JavaInternalDimensionID") = dimension.attr("JavaInternalDimensionID");
    m.attr("JavaDimension") = dimension.attr("JavaDimension");

    auto level = init_java_level(m);
    m.attr("JavaLevel") = level.attr("JavaLevel");

    return m;
}
