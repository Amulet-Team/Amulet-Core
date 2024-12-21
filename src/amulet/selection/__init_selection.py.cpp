#include <pybind11/operators.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <amulet/selection/box.hpp>
#include <amulet/selection/group.hpp>
#include <pybind11_extensions/collections.hpp>

namespace py = pybind11;

static void init_selection_box(py::class_<Amulet::SelectionBox> SelectionBox)
{
    // Constructors
    SelectionBox.def(
        py::init<
            std::tuple<std::int64_t, std::int64_t, std::int64_t>,
            std::tuple<std::int64_t, std::int64_t, std::int64_t>>(),
        py::doc(
            "Construct a new :class:`SelectionGroup` class from the given data.\n"
            "\n"
            ">>> SelectionGroup(SelectionBox((0, 0, 0), (1, 1, 1)))\n"
            ">>> SelectionGroup([\n"
            ">>>     SelectionBox((0, 0, 0), (1, 1, 1)),\n"
            ">>>     SelectionBox((1, 1, 1), (2, 2, 2))\n"
            ">>> ])\n"
            "\n"
            ":param selection_boxes: A :class:`SelectionBox` or iterable of :class:`SelectionBox` classes."),
        py::arg("point_1"),
        py::arg("point_2"));

    // Accessors
    SelectionBox.def(
        "point_1",
        &Amulet::SelectionBox::point_1,
        py::doc("The first value given to the constructor."));
    SelectionBox.def(
        "point_2",
        &Amulet::SelectionBox::point_2,
        py::doc("The second value given to the constructor."));
    SelectionBox.def(
        "min_x",
        &Amulet::SelectionBox::min_x,
        py::doc("The minimum x coordinate of the box."));
    SelectionBox.def(
        "min_y",
        &Amulet::SelectionBox::min_y,
        py::doc("The minimum y coordinate of the box."));
    SelectionBox.def(
        "min_z",
        &Amulet::SelectionBox::min_z,
        py::doc("The minimum z coordinate of the box."));
    SelectionBox.def(
        "max_x",
        &Amulet::SelectionBox::max_x,
        py::doc("The maximum x coordinate of the box."));
    SelectionBox.def(
        "max_y",
        &Amulet::SelectionBox::max_y,
        py::doc("The maximum y coordinate of the box."));
    SelectionBox.def(
        "max_z",
        &Amulet::SelectionBox::max_z,
        py::doc("The maximum z coordinate of the box."));
    SelectionBox.def(
        "min",
        &Amulet::SelectionBox::min,
        py::doc("The minimum coordinate of the box."));
    SelectionBox.def(
        "max",
        &Amulet::SelectionBox::max,
        py::doc("The maximum coordinate of the box."));

    // Shape and volume
    SelectionBox.def(
        "size_x",
        &Amulet::SelectionBox::size_x,
        py::doc("The length of the box in the x axis."));
    SelectionBox.def(
        "size_y",
        &Amulet::SelectionBox::size_y,
        py::doc("The length of the box in the y axis."));
    SelectionBox.def(
        "size_z",
        &Amulet::SelectionBox::size_z,
        py::doc("The length of the box in the z axis."));
    SelectionBox.def(
        "shape",
        &Amulet::SelectionBox::shape,
        py::doc(
            "The length of the box in the x, y and z axis.\n"
            "\n"
            ">>> SelectionBox((0, 0, 0), (1, 1, 1)).shape\n"
            "(1, 1, 1)"));
    SelectionBox.def(
        "volume",
        &Amulet::SelectionBox::volume,
        py::doc(
            "The number of blocks in the box.\n"
            "\n"
            ">>> SelectionBox((0, 0, 0), (1, 1, 1)).shape\n"
            "1"));

    // Contains and intersects
    SelectionBox.def(
        "contains_block",
        &Amulet::SelectionBox::contains_block,
        py::doc(
            "Is the block contained within the selection.\n"
            "\n"
            ">>> selection1: AbstractBaseSelection\n"
            ">>> (1, 2, 3) in selection1\n"
            "True\n"
            "\n"
            ":param x: The x coordinate of the block. Defined by the most negative corner.\n"
            ":param y: The y coordinate of the block. Defined by the most negative corner.\n"
            ":param z: The z coordinate of the block. Defined by the most negative corner.\n"
            ":return: True if the block is in the selection."),
        py::arg("x"),
        py::arg("y"),
        py::arg("z"));
    SelectionBox.def(
        "contains_point",
        &Amulet::SelectionBox::contains_point,
        py::doc(
            "Is the point contained within the selection.\n"
            "\n"
            ">>> selection1: AbstractBaseSelection\n"
            ">>> (1.5, 2.5, 3.5) in selection1\n"
            "True\n"
            "\n"
            ":param x: The x coordinate of the point.\n"
            ":param y: The y coordinate of the point.\n"
            ":param z: The z coordinate of the point.\n"
            ":return: True if the point is in the selection."),
        py::arg("x"),
        py::arg("y"),
        py::arg("z"));
    SelectionBox.def(
        "contains_box",
        &Amulet::SelectionBox::contains_box,
        py::doc(
            "Does the other SelectionBox other fit entirely within this SelectionBox.\n"
            "\n"
            ":param other: The SelectionBox to test.\n"
            ":return: True if other fits in self, False otherwise."),
        py::arg("other"));
    SelectionBox.def(
        "intersects",
        [](const Amulet::SelectionBox& self, const Amulet::SelectionBox& other) {
            return self.intersects(other);
        },
        py::doc(
            "Does this selection intersect ``other``.\n"
            "\n"
            ":param other: The other selection.\n"
            ":return: True if the selections intersect, False otherwise."),
        py::arg("other"));
    SelectionBox.def(
        "intersects",
        [](const Amulet::SelectionBox& self, const Amulet::SelectionGroup& other) {
            return self.intersects(other);
        },
        py::arg("other"));
    SelectionBox.def(
        "touches_or_intersects",
        &Amulet::SelectionBox::touches_or_intersects,
        py::doc(
            "Does this SelectionBox touch or intersect the other SelectionBox.\n"
            "\n"
            ":param other: The other SelectionBox.\n"
            ":return: True if the two :class:`SelectionBox` instances touch or intersect, False otherwise."),
        py::arg("other"));
    SelectionBox.def(
        "touches",
        &Amulet::SelectionBox::touches,
        py::doc(
            "Method to check if this instance of :class:`SelectionBox` touches but does not intersect another SelectionBox.\n"
            "\n"
            ":param other: The other SelectionBox\n"
            ":return: True if the two :class:`SelectionBox` instances touch, False otherwise"),
        py::arg("other"));

    // Transform
    SelectionBox.def(
        "translate",
        &Amulet::SelectionBox::translate,
        py::doc(
            "Create a new :class:`SelectionBox` based on this one with the coordinates moved by the given offset.\n"
            "\n"
            ":param x: The x offset.\n"
            ":param y: The y offset.\n"
            ":param z: The z offset.\n"
            ":return: The new selection with the given offset."),
        py::arg("x"),
        py::arg("y"),
        py::arg("z"));

    // Dunder methods
    SelectionBox.def(py::self < py::self);
    SelectionBox.def(py::self <= py::self);
    SelectionBox.def(py::self == py::self);
    SelectionBox.def(py::self >= py::self);
    SelectionBox.def(py::self > py::self);
    SelectionBox.def(
        "__repr__",
        [](const Amulet::SelectionBox& self) {
            return "SelectionBox(("
                + std::to_string(std::get<0>(self.point_1()))
                + ", "
                + std::to_string(std::get<1>(self.point_1()))
                + ", "
                + std::to_string(std::get<2>(self.point_1()))
                + "), ("
                + std::to_string(std::get<0>(self.point_2()))
                + ", "
                + std::to_string(std::get<1>(self.point_2()))
                + ", "
                + std::to_string(std::get<2>(self.point_2()))
                + "))";
        });
    SelectionBox.def(
        "__str__",
        [](const Amulet::SelectionBox& self) {
            return "(("
                + std::to_string(std::get<0>(self.point_1()))
                + ", "
                + std::to_string(std::get<1>(self.point_1()))
                + ", "
                + std::to_string(std::get<2>(self.point_1()))
                + "), ("
                + std::to_string(std::get<0>(self.point_2()))
                + ", "
                + std::to_string(std::get<1>(self.point_2()))
                + ", "
                + std::to_string(std::get<2>(self.point_2()))
                + "))";
        });
    SelectionBox.def(
        "__hash__",
        [](const Amulet::SelectionBox& self) {
            return py::hash(
                py::make_tuple(
                    py::cast(self.point_1()),
                    py::cast(self.point_2())));
        });
}

void init_selection_group(py::class_<Amulet::SelectionGroup> SelectionGroup)
{
    // Constructors
    SelectionGroup.def(
        py::init<>(),
        py::doc(
            "Create an empty SelectionGroup.\n"
            "\n"
            ">>> SelectionGroup()"));
    SelectionGroup.def(
        py::init<const Amulet::SelectionBox&>(),
        py::arg("box"),
        py::doc(
            "Create a SelectionGroup containing the given box.\n"
            "\n"
            ">>> SelectionGroup(SelectionBox((0, 0, 0), (1, 1, 1)))"));
    SelectionGroup.def(
        py::init(
            [](pybind11_extensions::Iterable<Amulet::SelectionBox> boxes) {
                return Amulet::SelectionGroup(boxes);
            }),
        py::arg("boxes"),
        py::doc(
            "Create a SelectionGroup from the boxes in the iterable.\n"
            "\n"
            ">>> SelectionGroup([\n"
            ">>> SelectionBox((0, 0, 0), (1, 1, 1)),\n"
            ">>> SelectionBox((1, 1, 1), (2, 2, 2))\n"
            ">>> ])\n"));

    // Accessors
    SelectionGroup.def_property_readonly(
        "selection_boxes",
        &Amulet::SelectionGroup::selection_boxes,
        py::doc(
            "An iterable of the :class:`SelectionBox` instances stored for this group."));

    // Bounds
    SelectionGroup.def_property_readonly(
        "min_x",
        &Amulet::SelectionGroup::min_x,
        py::doc(
            "The minimum x coordinate in the selection.\n"
            "\n"
            ":raises RuntimeError: If there are no boxes in the selection."));
    SelectionGroup.def_property_readonly(
        "min_y",
        &Amulet::SelectionGroup::min_y,
        py::doc(
            "The minimum y coordinate in the selection.\n"
            "\n"
            ":raises RuntimeError: If there are no boxes in the selection."));
    SelectionGroup.def_property_readonly(
        "min_z",
        &Amulet::SelectionGroup::min_z,
        py::doc(
            "The minimum z coordinate in the selection.\n"
            "\n"
            ":raises RuntimeError: If there are no boxes in the selection."));
    SelectionGroup.def_property_readonly(
        "max_x",
        &Amulet::SelectionGroup::max_x,
        py::doc(
            "The maximum x coordinate in the selection.\n"
            "\n"
            ":raises RuntimeError: If there are no boxes in the selection."));
    SelectionGroup.def_property_readonly(
        "max_y",
        &Amulet::SelectionGroup::max_y,
        py::doc(
            "The maximum y coordinate in the selection.\n"
            "\n"
            ":raises RuntimeError: If there are no boxes in the selection."));
    SelectionGroup.def_property_readonly(
        "max_z",
        &Amulet::SelectionGroup::max_z,
        py::doc(
            "The maximum z coordinate in the selection.\n"
            "\n"
            ":raises RuntimeError: If there are no boxes in the selection."));
    SelectionGroup.def_property_readonly(
        "min",
        &Amulet::SelectionGroup::min,
        py::doc(
            "The minimum x, y and z coordinates in the selection.\n"
            "\n"
            ":raises RuntimeError: If there are no boxes in the selection."));
    SelectionGroup.def_property_readonly(
        "max",
        &Amulet::SelectionGroup::max,
        py::doc(
            "The maximum x, y and z coordinates in the selection.\n"
            "\n"
            ":raises RuntimeError: If there are no boxes in the selection."));
    SelectionGroup.def_property_readonly(
        "bounds",
        &Amulet::SelectionGroup::bounds,
        py::doc(
            "The minimum and maximum x, y and z coordinates in the selection.\n"
            "\n"
            ":raises RuntimeError: If there are no boxes in the selection."));
    SelectionGroup.def_property_readonly(
        "bounding_box",
        &Amulet::SelectionGroup::bounding_box,
        py::doc(
            "A SelectionBox containing this entire selection.\n"
            "\n"
            ":raises RuntimeError: If there are no boxes in the selection."));

    // Contains and intersects
    SelectionGroup.def(
        "contains_block",
        &Amulet::SelectionGroup::contains_block,
        py::arg("x"),
        py::arg("y"),
        py::arg("z"),
        py::doc(
            "Is the block contained within the selection.\n"
            "\n"
            ">>> selection1: AbstractBaseSelection\n"
            ">>> (1, 2, 3) in selection1\n"
            "True\n"
            "\n"
            ":param x: The x coordinate of the block. Defined by the most negative corner.\n"
            ":param y: The y coordinate of the block. Defined by the most negative corner.\n"
            ":param z: The z coordinate of the block. Defined by the most negative corner.\n"
            ":return: True if the block is in the selection."));
    SelectionGroup.def(
        "contains_point",
        &Amulet::SelectionGroup::contains_point,
        py::arg("x"),
        py::arg("y"),
        py::arg("z"),
        py::doc(
            "Is the point contained within the selection.\n"
            "\n"
            ">>> selection1: AbstractBaseSelection\n"
            ">>> (1.5, 2.5, 3.5) in selection1\n"
            "True\n"
            "\n"
            ":param x: The x coordinate of the point.\n"
            ":param y: The y coordinate of the point.\n"
            ":param z: The z coordinate of the point.\n"
            ":return: True if the point is in the selection."));
    SelectionGroup.def(
        "intersects",
        [](const Amulet::SelectionGroup& self, const Amulet::SelectionBox& other) {
            return self.intersects(other);
        },
        py::arg("other"),
        py::doc(
            "Does this selection intersect ``other``.\n"
            "\n"
            ":param other: The other selection.\n"
            ":return: True if the selections intersect, False otherwise."));
    SelectionGroup.def(
        "intersects",
        [](const Amulet::SelectionGroup& self, const Amulet::SelectionGroup& other) {
            return self.intersects(other);
        },
        py::arg("other"));

    // Transform
    SelectionGroup.def(
        "translate",
        &Amulet::SelectionGroup::translate,
        py::arg("x"),
        py::arg("y"),
        py::arg("z"),
        py::doc(
            "Create a new :class:`SelectionGroup` based on this one with the coordinates moved by the given offset.\n"
            "\n"
            ":param x: The x offset.\n"
            ":param y: The y offset.\n"
            ":param z: The z offset.\n"
            ":return: The new selection with the given offset."));

    // Dunder methods
    SelectionGroup.def(
        "__repr__",
        [](const Amulet::SelectionGroup& self) {
            std::string out = "SelectionGroup([";
            bool comma = false;
            for (const auto& box : self.selection_boxes()) {
                if (comma) {
                    out += ", ";
                } else {
                    comma = true;
                }
                out += "SelectionBox((";
                out += std::to_string(std::get<0>(box.point_1()));
                out += ", ";
                out += std::to_string(std::get<1>(box.point_1()));
                out += ", ";
                out += std::to_string(std::get<2>(box.point_1()));
                out += "), (";
                out += std::to_string(std::get<0>(box.point_2()));
                out += ", ";
                out += std::to_string(std::get<1>(box.point_2()));
                out += ", ";
                out += std::to_string(std::get<2>(box.point_2()));
                out += "))";
            }
            out += "])";
            return out;
        });
    SelectionGroup.def(
        "__str__",
        [](const Amulet::SelectionGroup& self) {
            std::string out = "[";
            bool comma = false;
            for (const auto& box : self.selection_boxes()) {
                if (comma) {
                    out += ", ";
                } else {
                    comma = true;
                }
                out += "((";
                out += std::to_string(std::get<0>(box.point_1()));
                out += ", ";
                out += std::to_string(std::get<1>(box.point_1()));
                out += ", ";
                out += std::to_string(std::get<2>(box.point_1()));
                out += "), (";
                out += std::to_string(std::get<0>(box.point_2()));
                out += ", ";
                out += std::to_string(std::get<1>(box.point_2()));
                out += ", ";
                out += std::to_string(std::get<2>(box.point_2()));
                out += "))";
            }
            out += "]";
            return out;
        });
    SelectionGroup.def(
        "__iter__",
        [](const Amulet::SelectionGroup& self) {
            return py::make_iterator(self.selection_boxes());
        },
        py::doc("An iterable of all the :class:`SelectionBox` classes in the group."),
        py::keep_alive<0, 1>());
    SelectionGroup.def(
        py::self == py::self,
        py::doc(
            "Does the contents of this :class:`SelectionGroup` match the other :class:`SelectionGroup`.\n"
            "\n"
            "Note if the boxes do not exactly match this will return False even if the volume represented is the same.\n"
            "\n"
            ":param other: The other :class:`SelectionGroup` to compare with.\n"
            ":return: True if the boxes contained match."));
    SelectionGroup.def(
        "__bool__",
        &Amulet::SelectionGroup::operator bool,
        py::doc("The number of :class:`SelectionBox` classes in the group."));
    SelectionGroup.def(
        "__len__",
        &Amulet::SelectionGroup::size,
        py::doc("The number of :class:`SelectionBox` classes in the group."));
}

void init_selection(py::module m_parent)
{
    auto m = m_parent.def_submodule("selection");

    auto selection_box_module = m.def_submodule("box");
    auto selection_group_module = m.def_submodule("group");

    py::class_<Amulet::SelectionBox> SelectionBox(selection_box_module, "SelectionBox",
        "The SelectionBox class represents a single cuboid selection.\n"
        "\n"
        "When combined with :class:`~amulet.api.selection.SelectionGroup` it can represent any arbitrary shape.");
    py::class_<Amulet::SelectionGroup> SelectionGroup(selection_group_module, "SelectionGroup",
        "A container for zero or more :class:`SelectionBox` instances.\n"
        "\n"
        "This allows for non-rectangular and non-contiguous selections.");

    init_selection_box(SelectionBox);
    init_selection_group(SelectionGroup);

    m.attr("SelectionBox") = selection_box_module.attr("SelectionBox");
    m.attr("SelectionGroup") = selection_group_module.attr("SelectionGroup");
}
