#include <pybind11/pybind11.h>

namespace py = pybind11;

static void test_version_number()
{
}

static void test_version_range()
{
}

void init_test_version(py::module m_parent)
{
    auto m = m_parent.def_submodule("test_version_");
    m.def("test_version_number", &test_version_number);
    m.def("test_version_range", &test_version_range);
}
