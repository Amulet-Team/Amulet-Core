#include <pybind11/pybind11.h>

namespace py = pybind11;

static void test_block_entity_component()
{
}

void init_test_block_entity_component(py::module m_parent)
{
    auto m = m_parent.def_submodule("test_block_entity_component_");
    m.def("test_block_entity_component", &test_block_entity_component);
}
