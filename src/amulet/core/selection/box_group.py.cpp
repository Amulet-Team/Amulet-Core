#include <pybind11/operators.h>
#include <pybind11/pybind11.h>
#include <pybind11/typing.h>

#include <amulet/pybind11_extensions/collections.hpp>

#include <amulet/utils/matrix.hpp>

#include "box_group.hpp"
#include "shape_group.hpp"

namespace py = pybind11;
namespace pyext = Amulet::pybind11_extensions;

template <typename T, std::size_t N, typename... Ts>
struct PyTuple : PyTuple<T, N - 1, T, Ts...> { };

template <typename T, typename... Ts>
struct PyTuple<T, 0, Ts...> {
    using type = py::typing::Tuple<Ts...>;
};

template <typename arrayT>
PyTuple<typename arrayT::value_type, std::tuple_size_v<arrayT>>::type wrap_array(const arrayT& arr)
{
    auto t = py::tuple(3);
    for (std::uint8_t i = 0; i < 3; i++) {
        t[i] = py::cast(arr[i]);
    }
    return t;
}

void init_selection_box_group(py::classh<Amulet::SelectionBoxGroup> SelectionBoxGroup)
{
    // Constructors
    SelectionBoxGroup.def(
        py::init<>(),
        py::doc(
            "Create an empty SelectionBoxGroup.\n"
            "\n"
            ">>> SelectionBoxGroup()"));
    SelectionBoxGroup.def(
        py::init(
            [](const Amulet::SelectionShapeGroup& shapes) {
                return shapes.voxelise();
            }),
        py::arg("shape_group"));
    SelectionBoxGroup.def(
        py::init(
            [](pyext::collections::Iterable<const Amulet::SelectionBox&> boxes) {
                return Amulet::SelectionBoxGroup(boxes.begin(), boxes.end());
            }),
        py::arg("boxes"),
        py::doc(
            "Create a SelectionBoxGroup from the boxes in the iterable.\n"
            "\n"
            ">>> SelectionBoxGroup([\n"
            ">>>     SelectionBox(0, 0, 0, 1, 1, 1),\n"
            ">>>     SelectionBox(1, 1, 1, 1, 1, 1)\n"
            ">>> ])\n"));

    // Accessors
    SelectionBoxGroup.def_property_readonly(
        "boxes",
        py::cpp_function(
            [](const Amulet::SelectionBoxGroup& self) {
                return py::make_iterator(self.get_boxes().begin(), self.get_boxes().end());
            },
            py::keep_alive<0, 1>()),
        py::doc("An iterator of the :class:`SelectionBox` instances stored for this group."));

    // Bounds
    SelectionBoxGroup.def_property_readonly(
        "min_x",
        &Amulet::SelectionBoxGroup::min_x,
        py::doc(
            "The minimum x coordinate in the selection.\n"
            "\n"
            ":raises RuntimeError: If there are no boxes in the selection."));
    SelectionBoxGroup.def_property_readonly(
        "min_y",
        &Amulet::SelectionBoxGroup::min_y,
        py::doc(
            "The minimum y coordinate in the selection.\n"
            "\n"
            ":raises RuntimeError: If there are no boxes in the selection."));
    SelectionBoxGroup.def_property_readonly(
        "min_z",
        &Amulet::SelectionBoxGroup::min_z,
        py::doc(
            "The minimum z coordinate in the selection.\n"
            "\n"
            ":raises RuntimeError: If there are no boxes in the selection."));
    SelectionBoxGroup.def_property_readonly(
        "max_x",
        &Amulet::SelectionBoxGroup::max_x,
        py::doc(
            "The maximum x coordinate in the selection.\n"
            "\n"
            ":raises RuntimeError: If there are no boxes in the selection."));
    SelectionBoxGroup.def_property_readonly(
        "max_y",
        &Amulet::SelectionBoxGroup::max_y,
        py::doc(
            "The maximum y coordinate in the selection.\n"
            "\n"
            ":raises RuntimeError: If there are no boxes in the selection."));
    SelectionBoxGroup.def_property_readonly(
        "max_z",
        &Amulet::SelectionBoxGroup::max_z,
        py::doc(
            "The maximum z coordinate in the selection.\n"
            "\n"
            ":raises RuntimeError: If there are no boxes in the selection."));
    SelectionBoxGroup.def_property_readonly(
        "min",
        [](const Amulet::SelectionBoxGroup& self) { return wrap_array(self.min()); },
        py::doc(
            "The minimum x, y and z coordinates in the selection.\n"
            "\n"
            ":raises RuntimeError: If there are no boxes in the selection."));
    SelectionBoxGroup.def_property_readonly(
        "max",
        [](const Amulet::SelectionBoxGroup& self) { return wrap_array(self.max()); },
        py::doc(
            "The maximum x, y and z coordinates in the selection.\n"
            "\n"
            ":raises RuntimeError: If there are no boxes in the selection."));
    SelectionBoxGroup.def_property_readonly(
        "bounds",
        [](const Amulet::SelectionBoxGroup& self) {
            auto [point_1, point_2] = self.bounds();
            return std::make_pair(
                wrap_array(point_1),
                wrap_array(point_2));
        },
        py::doc(
            "The minimum and maximum x, y and z coordinates in the selection.\n"
            "\n"
            ":raises RuntimeError: If there are no boxes in the selection."));
    SelectionBoxGroup.def_property_readonly(
        "bounding_box",
        &Amulet::SelectionBoxGroup::bounding_box,
        py::doc(
            "A SelectionBox containing this entire selection.\n"
            "\n"
            ":raises RuntimeError: If there are no boxes in the selection."));

    // Contains and intersects
    SelectionBoxGroup.def(
        "contains_block",
        &Amulet::SelectionBoxGroup::contains_block,
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
    SelectionBoxGroup.def(
        "contains_point",
        &Amulet::SelectionBoxGroup::contains_point,
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
    SelectionBoxGroup.def(
        "intersects",
        [](const Amulet::SelectionBoxGroup& self, const Amulet::SelectionBox& other) {
            return self.intersects(other);
        },
        py::arg("other"),
        py::doc(
            "Does this selection intersect ``other``.\n"
            "\n"
            ":param other: The other selection.\n"
            ":return: True if the selections intersect, False otherwise."));
    SelectionBoxGroup.def(
        "intersects",
        [](const Amulet::SelectionBoxGroup& self, const Amulet::SelectionBoxGroup& other) {
            return self.intersects(other);
        },
        py::arg("other"));

    // Transform
    SelectionBoxGroup.def(
        "translate",
        &Amulet::SelectionBoxGroup::translate,
        py::arg("dx"),
        py::arg("dy"),
        py::arg("dz"),
        py::doc(
            "Create a new :class:`SelectionBoxGroup` based on this one with the coordinates moved by the given offset.\n"
            "\n"
            ":param dx: The x offset.\n"
            ":param dy: The y offset.\n"
            ":param dz: The z offset.\n"
            ":return: The new selection with the given offset."));
    SelectionBoxGroup.def(
        "transform",
        &Amulet::SelectionBoxGroup::transform,
        py::arg("matrix"),
        py::doc("Transform the boxes in this group by the given transformation matrix."));

    // Dunder methods
    SelectionBoxGroup.def(
        "__repr__",
        [](const Amulet::SelectionBoxGroup& self) {
            std::string out = "SelectionBoxGroup([";
            bool comma = false;
            for (const auto& box : self.get_boxes()) {
                if (comma) {
                    out += ", ";
                } else {
                    comma = true;
                }
                out += "SelectionBox(";
                out += std::to_string(box.min_x());
                out += ", ";
                out += std::to_string(box.min_y());
                out += ", ";
                out += std::to_string(box.min_z());
                out += ", ";
                out += std::to_string(box.size_x());
                out += ", ";
                out += std::to_string(box.size_y());
                out += ", ";
                out += std::to_string(box.size_z());
                out += ")";
            }
            out += "])";
            return out;
        });
    SelectionBoxGroup.def(
        "__str__",
        [](const Amulet::SelectionBoxGroup& self) {
            std::string out = "[";
            bool comma = false;
            for (const auto& box : self.get_boxes()) {
                if (comma) {
                    out += ", ";
                } else {
                    comma = true;
                }
                out += "(";
                out += std::to_string(box.min_x());
                out += ", ";
                out += std::to_string(box.min_y());
                out += ", ";
                out += std::to_string(box.min_z());
                out += ", ";
                out += std::to_string(box.size_x());
                out += ", ";
                out += std::to_string(box.size_y());
                out += ", ";
                out += std::to_string(box.size_z());
                out += ")";
            }
            out += "]";
            return out;
        });
    SelectionBoxGroup.def(
        "__iter__",
        [](const Amulet::SelectionBoxGroup& self) {
            return py::make_iterator(self.get_boxes());
        },
        py::doc("An iterable of all the :class:`SelectionBox` classes in the group."),
        py::keep_alive<0, 1>());
    SelectionBoxGroup.def(
        py::self == py::self,
        py::doc(
            "Does the contents of this :class:`SelectionBoxGroup` match the other :class:`SelectionBoxGroup`.\n"
            "\n"
            "Note if the boxes do not exactly match this will return False even if the volume represented is the same.\n"
            "\n"
            ":param other: The other :class:`SelectionBoxGroup` to compare with.\n"
            ":return: True if the boxes contained match."));
    SelectionBoxGroup.def(
        "__bool__",
        &Amulet::SelectionBoxGroup::operator bool,
        py::doc("Are there any selections in the group."));
    SelectionBoxGroup.def(
        "__len__",
        &Amulet::SelectionBoxGroup::count,
        py::doc("The number of :class:`SelectionBox` classes in the group."));
}
