#include <pybind11/pybind11.h>
#include <pybind11_extensions/py_module.hpp>
namespace py = pybind11;

void init_section_array_map(py::module);
void init_block_component(py::module);

void init_chunk_components(py::module m_parent) {
    auto m = pybind11_extensions::def_subpackage(m_parent, "chunk_components");
    init_section_array_map(m);
    init_block_component(m);
}
