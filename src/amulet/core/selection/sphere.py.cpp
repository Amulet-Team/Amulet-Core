#include <pybind11/pybind11.h>

#include "sphere.hpp"

namespace py = pybind11;

py::object init_selection_sphere(py::module m_parent)
{
    auto m = m_parent.def_submodule("sphere");
    py::classh<Amulet::SelectionSphere, Amulet::SelectionShape> SelectionSphere(m, "SelectionSphere",
        "The SelectionSphere class represents a single spherical selection.");
    SelectionSphere.def(
        py::init<double, double, double, double>(),
        py::arg("x"),
        py::arg("y"),
        py::arg("z"),
        py::arg("radius"));
    SelectionSphere.def_property_readonly(
        "x",
        &Amulet::SelectionSphere::get_x);
    SelectionSphere.def_property_readonly(
        "y",
        &Amulet::SelectionSphere::get_y);
    SelectionSphere.def_property_readonly(
        "z",
        &Amulet::SelectionSphere::get_z);
    SelectionSphere.def_property_readonly(
        "radius",
        &Amulet::SelectionSphere::get_radius);
    SelectionSphere.def(
        "translate",
        &Amulet::SelectionSphere::translate,
        py::doc(
            "Create a new :class:`SelectionSphere` based on this one with the coordinates moved by the given offset.\n"
            "\n"
            ":param dx: The x offset.\n"
            ":param dy: The y offset.\n"
            ":param dz: The z offset.\n"
            ":return: The new selection with the given offset."),
        py::arg("dx"),
        py::arg("dy"),
        py::arg("dz"));

    return SelectionSphere;
}
