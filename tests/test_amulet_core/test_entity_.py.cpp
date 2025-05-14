#include <pybind11/pybind11.h>

namespace py = pybind11;

static void test_entity()
{

}

void init_test_entity(py::module m_parent)
{
    auto m = m_parent.def_submodule("test_entity_");
    m.def("test_entity", &test_entity);
}
