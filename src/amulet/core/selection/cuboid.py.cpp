#include <pybind11/pybind11.h>

#include "cuboid.hpp"

namespace py = pybind11;

py::object init_selection_cuboid(py::module m_parent)
{
    auto m = m_parent.def_submodule("cuboid");
    std::string module_name = m.attr("__name__").cast<std::string>();

    py::classh<Amulet::SelectionCuboid, Amulet::SelectionShape> SelectionCuboid(m, "SelectionCuboid",
        "The SelectionCuboid class represents a single spherical selection.");

    SelectionCuboid.def(
        py::init<double, double, double, double, double, double>(),
        py::arg("min_x"),
        py::arg("min_y"),
        py::arg("min_z"),
        py::arg("size_x"),
        py::arg("size_y"),
        py::arg("size_z"));
    SelectionCuboid.def(
        py::init<const Amulet::Matrix4x4&>(),
        py::arg("matrix"));

    SelectionCuboid.def(
        "translate",
        &Amulet::SelectionCuboid::translate_cuboid,
        py::doc(
            "Create a new :class:`SelectionCuboid` based on this one with the coordinates moved by the given offset.\n"
            "\n"
            ":param dx: The x offset.\n"
            ":param dy: The y offset.\n"
            ":param dz: The z offset.\n"
            ":return: The new selection with the given offset."),
        py::arg("dx"),
        py::arg("dy"),
        py::arg("dz"));

    SelectionCuboid.def(
        "transform",
        &Amulet::SelectionCuboid::transform_cuboid,
        py::doc(
            "Create a new :class:`SelectionCuboid` based on this one transformed by the given matrix.\n"
            "\n"
            ":param matrix: The matrix to transform by.\n"
            ":return: The new selection with the added transform."),
        py::arg("matrix"));

    auto repr = py::module::import("builtins").attr("repr");
    SelectionCuboid.def(
        "__repr__",
        [module_name, repr](const Amulet::SelectionCuboid& self) {
            return module_name + ".SelectionCuboid(" + repr(py::cast(self.get_matrix(), py::return_value_policy::reference)).cast<std::string>() + ")";
        });

    return SelectionCuboid;
}
