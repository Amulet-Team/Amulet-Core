#include <pybind11/pybind11.h>
#include <pybind11/typing.h>

#include "shape_group.hpp"

namespace py = pybind11;

py::object init_selection_shape_group(py::module m_parent)
{
    auto m = m_parent.def_submodule("shape_group");
    py::classh<Amulet::SelectionShapeGroup> SelectionShapeGroup(m, "SelectionShapeGroup",
        "A group of selection shapes.");

    // Constructors
    SelectionShapeGroup.def(
        py::init<>(),
        py::doc(
            "Create an empty SelectionShapeGroup.\n"
            "\n"
            ">>> SelectionShapeGroup()"));
    SelectionShapeGroup.def(
        py::init(
            [](pyext::collections::Iterable<const Amulet::SelectionShape&> py_shapes) {
                std::vector<std::unique_ptr<const Amulet::SelectionShape>> shapes;
                for (const auto& shape : py_shapes) {
                    shapes.push_back(shape.copy());
                }
                return Amulet::SelectionShapeGroup(std::move(shapes));
            }),
        py::arg("shapes"),
        py::doc(
            "Create a SelectionShapeGroup from the selections in the iterable.\n"
            "\n"
            ">>> SelectionShapeGroup([\n"
            ">>>     SelectionBox(0, 0, 0, 1, 1, 1),\n"
            ">>>     SelectionBox(1, 1, 1, 1, 1, 1)\n"
            ">>> ])\n"));

    // Accessors
    SelectionShapeGroup.def_property_readonly(
        "shapes",
        py::cpp_function(
            [](const Amulet::SelectionShapeGroup& self) {
                return py::make_iterator(self.get_shapes());
            },
            py::keep_alive<0, 1>()),
        py::doc("An iterator of the :class:`SelectionShape` instances stored for this group."));

    // Dunder methods
    SelectionShapeGroup.def(
        "__iter__",
        [](const Amulet::SelectionShapeGroup& self) {
            return py::make_iterator(self.get_shapes());
        },
        py::doc("An iterable of all the :class:`SelectionShape` classes in the group."),
        py::keep_alive<0, 1>());
    SelectionShapeGroup.def(
        "__bool__",
        &Amulet::SelectionShapeGroup::operator bool,
        py::doc("Are there any selections in the group."));
    SelectionShapeGroup.def(
        "__len__",
        &Amulet::SelectionShapeGroup::count,
        py::doc("The number of :class:`SelectionShape` classes in the group."));

    return SelectionShapeGroup;
}
