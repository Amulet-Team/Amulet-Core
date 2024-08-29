#include <pybind11/pybind11.h>
namespace py = pybind11;

void init_section_array_map(py::module);
void init_block_component(py::module);

void init_chunk_components(py::module chunk_components_module) {
    init_section_array_map(chunk_components_module);
    init_block_component(chunk_components_module);
}
