#include <pybind11/pybind11.h>

namespace py = pybind11;

static void test_section_array_map()
{
}

void init_test_section_array_map(py::module m_parent)
{
    auto m = m_parent.def_submodule("test_section_array_map_");
    m.def("test_section_array_map", &test_section_array_map);
}
