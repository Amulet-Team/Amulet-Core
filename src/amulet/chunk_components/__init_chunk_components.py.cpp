#include <pybind11/pybind11.h>
namespace py = pybind11;

void init_section_array_map(py::module);
void init_block_component(py::module);

void init_chunk_components(py::module m_parent) {
    auto m = m_parent.def_submodule("chunk_components");
    init_section_array_map(m);
    init_block_component(m);
}
