#include <pybind11/operators.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/typing.h>

#include "box_group.hpp"
#include "shape.hpp"

namespace py = pybind11;

py::object init_selection_shape(py::module m_parent)
{
    auto m = m_parent.def_submodule("shape");
    py::classh<Amulet::SelectionShape> SelectionShape(m, "SelectionShape",
        "A base class for selection classes.");

    SelectionShape.def_property(
        "matrix",
        &Amulet::SelectionShape::get_matrix,
        &Amulet::SelectionShape::set_matrix);

    SelectionShape.def(
        "serialise",
        &Amulet::SelectionShape::serialise,
        py::doc("Convert the class to human readable plain text."));
    SelectionShape.def_static(
        "deserialise",
        static_cast<std::unique_ptr<Amulet::SelectionShape> (*)(std::string_view)>(
            &Amulet::SelectionShape::deserialise),
        py::arg("s"),
        py::doc("Deserialise the serialised data back to an object."));

    SelectionShape.def(
        "voxelise",
        &Amulet::SelectionShape::voxelise,
        py::doc("Convert the selection to a SelectionBoxGroup."));

    SelectionShape.def(
        "translate",
        &Amulet::SelectionShape::translate,
        py::arg("dx"),
        py::arg("dy"),
        py::arg("dz"),
        py::doc("Translate the shape by the given amount"));

    SelectionShape.def(
        "transform",
        &Amulet::SelectionShape::transform,
        py::arg("matrix"),
        py::doc("Translate the shape by the given matrix"));

    SelectionShape.def(
        "almost_equal",
        &Amulet::SelectionShape::almost_equal,
        py::arg("other"),
        py::doc("Check if this shape is equal or almost equal to another shape."));
    SelectionShape.def(py::self == py::self);

    return SelectionShape;
}
