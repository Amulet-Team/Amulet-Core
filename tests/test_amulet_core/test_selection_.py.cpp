#include <pybind11/pybind11.h>

namespace py = pybind11;

static void test_selection_box()
{
}

static void test_selection_group()
{
}

void init_test_selection(py::module m_parent)
{
    auto m = m_parent.def_submodule("test_selection_");
    m.def("test_selection_box", &test_selection_box);
    m.def("test_selection_group", &test_selection_group);
}
