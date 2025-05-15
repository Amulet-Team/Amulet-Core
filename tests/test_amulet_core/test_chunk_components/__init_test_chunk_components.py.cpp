#include <pybind11/pybind11.h>

#include <amulet/pybind11_extensions/py_module.hpp>

namespace py = pybind11;
namespace pyext = Amulet::pybind11_extensions;

void init_test_biome_3d_component(py::module);
void init_test_block_component(py::module);
void init_test_block_entity_component(py::module);
void init_test_section_array_map(py::module);

void init_test_chunk_components(py::module m_parent)
{
    auto m = pyext::def_subpackage(m_parent, "test_chunk_components");
    init_test_biome_3d_component(m);
    init_test_block_component(m);
    init_test_block_entity_component(m);
    init_test_section_array_map(m);
}
