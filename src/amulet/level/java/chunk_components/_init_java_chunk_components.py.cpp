#include <string>
#include <vector>
#include <pybind11/pybind11.h>
namespace py = pybind11;

void init_data_version_component(py::module);

void init_java_chunk_components(py::module java_chunk_components_module) {
    auto data_version_component_module = java_chunk_components_module.def_submodule("data_version_component");
    init_data_version_component(data_version_component_module);
}
