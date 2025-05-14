#include <pybind11/pybind11.h>

namespace py = pybind11;

static void test_block()
{

}

static void test_block_stack()
{

}

void init_test_block(py::module m_parent)
{
    auto m = m_parent.def_submodule("test_block_");
    m.def("test_block", &test_block);
    m.def("test_block_stack", &test_block_stack);
}
