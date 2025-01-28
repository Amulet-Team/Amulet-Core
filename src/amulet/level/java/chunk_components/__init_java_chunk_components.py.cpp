#include <pybind11/pybind11.h>

#include <string>
#include <vector>

#include <pybind11_extensions/py_module.hpp>

namespace py = pybind11;

void init_data_version_component(py::module);
void init_java_raw_chunk_component(py::module);

void init_java_chunk_components(py::module m_parent)
{
    auto m = pybind11_extensions::def_subpackage(m_parent, "chunk_components");
    init_data_version_component(m);
    init_java_raw_chunk_component(m);
}
