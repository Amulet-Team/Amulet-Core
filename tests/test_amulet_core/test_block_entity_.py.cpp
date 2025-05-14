#include <pybind11/pybind11.h>

namespace py = pybind11;

static void test_block_entity()
{

}

void init_test_block_entity(py::module m_parent)
{
    auto m = m_parent.def_submodule("test_block_entity_");
    m.def("test_block_entity", &test_block_entity);
}
