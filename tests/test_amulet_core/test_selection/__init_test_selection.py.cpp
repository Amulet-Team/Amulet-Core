#include <pybind11/pybind11.h>

#include <amulet/pybind11_extensions/py_module.hpp>

namespace py = pybind11;
namespace pyext = Amulet::pybind11_extensions;

void init_test_selection_box(py::module);
void init_test_selection_box_group(py::module);
void init_test_selection_shape_group(py::module);
void init_test_selection_cuboid(py::module);
void init_test_selection_ellipsoid(py::module);

void init_test_selection(py::module m_parent)
{
    auto m = pyext::def_subpackage(m_parent, "test_selection");
    init_test_selection_box(m);
    init_test_selection_box_group(m);
    init_test_selection_shape_group(m);
    init_test_selection_cuboid(m);
    init_test_selection_ellipsoid(m);
}
