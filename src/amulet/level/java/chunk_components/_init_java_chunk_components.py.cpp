#include <string>
#include <vector>
#include <pybind11/pybind11.h>
namespace py = pybind11;

void init_data_version_component(py::module);
void init_java_raw_chunk_component(py::module);

void init_java_chunk_components(py::module java_chunk_components_module) {
    init_data_version_component(java_chunk_components_module);
    init_java_raw_chunk_component(java_chunk_components_module);
}
