#include <pybind11/pybind11.h>

namespace py = pybind11;

static void test_biome()
{

}

void init_test_biome(py::module m_parent)
{
    auto m = m_parent.def_submodule("test_biome_");
    m.def("test_biome", &test_biome);
}
