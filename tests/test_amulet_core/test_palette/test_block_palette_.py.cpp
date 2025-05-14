#include <pybind11/pybind11.h>

namespace py = pybind11;

static void test_block_palette()
{
}

void init_test_block_palette(py::module m_parent)
{
    auto m = m_parent.def_submodule("test_block_palette_");
    m.def("test_block_palette", &test_block_palette);
}
