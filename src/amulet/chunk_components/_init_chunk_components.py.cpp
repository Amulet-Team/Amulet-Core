#include <pybind11/pybind11.h>
namespace py = pybind11;

void init_section_array_map(py::module);

void init_chunk_components(py::module chunk_components_module) {
    auto section_array_map_module = chunk_components_module.def_submodule("section_array_map");
    init_section_array_map(section_array_map_module);
}
