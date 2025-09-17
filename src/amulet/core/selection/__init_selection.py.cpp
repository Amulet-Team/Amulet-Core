#include <pybind11/pybind11.h>

#include <amulet/pybind11_extensions/py_module.hpp>

#include "box.hpp"
#include "box_group.hpp"
#include "shape_group.hpp"

namespace py = pybind11;
namespace pyext = Amulet::pybind11_extensions;

void init_selection_box(py::classh<Amulet::SelectionBox>);
void init_selection_box_group(py::classh<Amulet::SelectionBoxGroup>);
py::object init_selection_shape(py::module);
void init_selection_shape_group(py::module, py::classh<Amulet::SelectionShapeGroup>);
py::object init_selection_cuboid(py::module m_parent);
py::object init_selection_ellipsoid(py::module m_parent);

void init_selection(py::module m_parent)
{
    auto m = pyext::def_subpackage(m_parent, "selection");

    auto selection_box_module = m.def_submodule("box");
    auto selection_box_group_module = m.def_submodule("box_group");
    auto selection_shape_group_module = m.def_submodule("shape_group");

    // Low level selection
    // These classes must be defined before methods can be added
    py::classh<Amulet::SelectionBox> SelectionBox(selection_box_module, "SelectionBox",
        "The SelectionBox class represents a single cuboid selection.\n"
        "\n"
        "When combined with :class:`~amulet.api.selection.SelectionBoxGroup` it can represent any arbitrary shape.");
    py::classh<Amulet::SelectionBoxGroup> SelectionBoxGroup(selection_box_group_module, "SelectionBoxGroup",
        "A container for zero or more :class:`SelectionBox` instances.\n"
        "\n"
        "This allows for non-rectangular and non-contiguous selections.");
    py::classh<Amulet::SelectionShapeGroup> SelectionShapeGroup(selection_shape_group_module, "SelectionShapeGroup",
        "A group of selection shapes.");

    // Shape base class
    m.attr("SelectionShape") = init_selection_shape(m);

    // Init box classes
    init_selection_box(SelectionBox);
    init_selection_box_group(SelectionBoxGroup);

    m.attr("SelectionBox") = SelectionBox;
    m.attr("SelectionBoxGroup") = SelectionBoxGroup;
    m.attr("SelectionShapeGroup") = SelectionShapeGroup;

    // Init shape classes
    init_selection_shape_group(selection_shape_group_module, SelectionShapeGroup);
    m.attr("SelectionCuboid") = init_selection_cuboid(m);
    m.attr("SelectionEllipsoid") = init_selection_ellipsoid(m);
}
