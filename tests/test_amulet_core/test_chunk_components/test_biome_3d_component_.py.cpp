#include <pybind11/pybind11.h>

namespace py = pybind11;

static void test_biome_3d_component()
{
}

void init_test_biome_3d_component(py::module m_parent)
{
    auto m = m_parent.def_submodule("test_biome_3d_component_");
    m.def("test_biome_3d_component", &test_biome_3d_component);
}
