#include <string>
#include <vector>
#include <pybind11/pybind11.h>
namespace py = pybind11;

void init_data_version_component(py::module);
void init_java_raw_chunk_component(py::module);

void init_java_chunk_components(py::module m_parent) {
    auto m = m_parent.def_submodule("chunk_components");
    init_data_version_component(m);
    init_java_raw_chunk_component(m);
}
