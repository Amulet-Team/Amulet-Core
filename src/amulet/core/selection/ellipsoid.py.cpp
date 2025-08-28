#include <pybind11/pybind11.h>

#include "ellipsoid.hpp"

namespace py = pybind11;

py::object init_selection_ellipsoid(py::module m_parent)
{
    auto m = m_parent.def_submodule("ellipsoid");
    std::string module_name = m.attr("__name__").cast<std::string>();

    py::classh<Amulet::SelectionEllipsoid, Amulet::SelectionShape> SelectionEllipsoid(m, "SelectionEllipsoid",
        "The SelectionEllipsoid class represents a single ellipsoid selection.");

    SelectionEllipsoid.def(
        py::init<double, double, double, double>(),
        py::arg("x"),
        py::arg("y"),
        py::arg("z"),
        py::arg("radius"));
    SelectionEllipsoid.def(
        py::init<const Amulet::Matrix4x4&>(),
        py::arg("matrix"));

    SelectionEllipsoid.def(
        "translate",
        &Amulet::SelectionEllipsoid::translate_ellipsoid,
        py::doc(
            "Create a new :class:`SelectionEllipsoid` based on this one with the coordinates moved by the given offset.\n"
            "\n"
            ":param dx: The x offset.\n"
            ":param dy: The y offset.\n"
            ":param dz: The z offset.\n"
            ":return: The new selection with the given offset."),
        py::arg("dx"),
        py::arg("dy"),
        py::arg("dz"));

    SelectionEllipsoid.def(
        "transform",
        &Amulet::SelectionEllipsoid::transform_ellipsoid,
        py::doc(
            "Create a new :class:`SelectionEllipsoid` based on this one transformed by the given matrix.\n"
            "\n"
            ":param matrix: The matrix to transform by.\n"
            ":return: The new selection with the added transform."),
        py::arg("matrix"));

    auto repr = py::module::import("builtins").attr("repr");
    SelectionEllipsoid.def(
        "__repr__",
        [module_name, repr](const Amulet::SelectionEllipsoid& self) {
            return module_name + ".SelectionEllipsoid(" + repr(py::cast(self.get_matrix(), py::return_value_policy::reference)).cast<std::string>() + ")";
        });

    return SelectionEllipsoid;
}
