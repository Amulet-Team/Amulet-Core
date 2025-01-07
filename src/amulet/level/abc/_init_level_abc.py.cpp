#include <string>
#include <pybind11/pybind11.h>
#include <pybind11_extensions/py_module.hpp>
namespace py = pybind11;

py::module init_chunk_handle(py::module);
py::module init_dimension(py::module);

py::module init_level_abc(py::module m_parent) {
    auto m = pybind11_extensions::def_subpackage(m_parent, "abc");

    auto m_chunk_handle = init_chunk_handle(m);
    m.attr("ChunkHandle") = m_chunk_handle.attr("ChunkHandle");

    auto m_dimension = init_dimension(m);
    m.attr("Dimension") = m_dimension.attr("Dimension");

    return m;
}
