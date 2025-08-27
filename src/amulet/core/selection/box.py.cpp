#include <pybind11/operators.h>
#include <pybind11/pybind11.h>
#include <pybind11/typing.h>

#include <amulet/utils/matrix.hpp>

#include "box.hpp"
#include "box_group.hpp"

namespace py = pybind11;

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

void init_selection_box(py::classh<Amulet::SelectionBox> SelectionBox)
{
    // Constructors
    SelectionBox.def(
        py::init<
            std::int64_t,
            std::int64_t,
            std::int64_t,
            std::uint64_t,
            std::uint64_t,
            std::uint64_t>(),
        py::doc(
            "Construct a new SelectionBox instance.\n"
            "\n"
            ">>> # a selection box that selects one block.\n"
            ">>> box = SelectionBox(0, 0, 0, 1, 1, 1)\n"
            "\n"
            ":param min_x: The minimum x coordinate of the box.\n"
            ":param min_y: The minimum y coordinate of the box.\n"
            ":param min_z: The minimum z coordinate of the box.\n"
            ":param size_x: The size of the box in the x axis.\n"
            ":param size_y: The size of the box in the y axis.\n"
            ":param size_z: The size of the box in the z axis."),
        py::arg("min_x"),
        py::arg("min_y"),
        py::arg("min_z"),
        py::arg("size_x"),
        py::arg("size_y"),
        py::arg("size_z"));

    SelectionBox.def(
        py::init(
            [](
                py::typing::Tuple<std::int64_t, std::int64_t, std::int64_t> point_1,
                py::typing::Tuple<std::int64_t, std::int64_t, std::int64_t> point_2) {
                return Amulet::SelectionBox(
                    {
                        py::cast<std::int64_t>(point_1[0]),
                        py::cast<std::int64_t>(point_1[1]),
                        py::cast<std::int64_t>(point_1[2]),
                    },
                    {
                        py::cast<std::int64_t>(point_2[0]),
                        py::cast<std::int64_t>(point_2[1]),
                        py::cast<std::int64_t>(point_2[2]),
                    });
            }),
        py::doc(
            "Construct a new SelectionBox instance.\n"
            "\n"
            ">>> # a selection box that selects one block.\n"
            ">>> box = SelectionBox((0, 0, 0), (1, 1, 1))\n"
            "\n"
            ":param point_1: The first coordinate of the box.\n"
            ":param point_2: The second coordinate of the box."),
        py::arg("point_1"),
        py::arg("point_2"));

    // Accessors
    SelectionBox.def_property_readonly(
        "min_x",
        &Amulet::SelectionBox::min_x,
        py::doc("The minimum x coordinate of the box."));
    SelectionBox.def_property_readonly(
        "min_y",
        &Amulet::SelectionBox::min_y,
        py::doc("The minimum y coordinate of the box."));
    SelectionBox.def_property_readonly(
        "min_z",
        &Amulet::SelectionBox::min_z,
        py::doc("The minimum z coordinate of the box."));
    SelectionBox.def_property_readonly(
        "max_x",
        &Amulet::SelectionBox::max_x,
        py::doc("The maximum x coordinate of the box."));
    SelectionBox.def_property_readonly(
        "max_y",
        &Amulet::SelectionBox::max_y,
        py::doc("The maximum y coordinate of the box."));
    SelectionBox.def_property_readonly(
        "max_z",
        &Amulet::SelectionBox::max_z,
        py::doc("The maximum z coordinate of the box."));
    SelectionBox.def_property_readonly(
        "min",
        [](const Amulet::SelectionBox& self) { return wrap_array(self.min()); },
        py::doc("The minimum coordinate of the box."));
    SelectionBox.def_property_readonly(
        "max",
        [](const Amulet::SelectionBox& self) { return wrap_array(self.max()); },
        py::doc("The maximum coordinate of the box."));

    // Shape and volume
    SelectionBox.def_property_readonly(
        "size_x",
        &Amulet::SelectionBox::size_x,
        py::doc("The length of the box in the x axis."));
    SelectionBox.def_property_readonly(
        "size_y",
        &Amulet::SelectionBox::size_y,
        py::doc("The length of the box in the y axis."));
    SelectionBox.def_property_readonly(
        "size_z",
        &Amulet::SelectionBox::size_z,
        py::doc("The length of the box in the z axis."));
    SelectionBox.def_property_readonly(
        "shape",
        [](const Amulet::SelectionBox& self) { return wrap_array(self.shape()); },
        py::doc(
            "The length of the box in the x, y and z axis.\n"
            "\n"
            ">>> SelectionBox(0, 0, 0, 1, 1, 1).shape\n"
            "(1, 1, 1)"));
    SelectionBox.def_property_readonly(
        "volume",
        &Amulet::SelectionBox::volume,
        py::doc(
            "The number of blocks in the box.\n"
            "\n"
            ">>> SelectionBox(0, 0, 0, 1, 1, 1).volume\n"
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
        [](const Amulet::SelectionBox& self, const Amulet::SelectionBoxGroup& other) {
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
            ":param dx: The x offset.\n"
            ":param dy: The y offset.\n"
            ":param dz: The z offset.\n"
            ":return: The new selection with the given offset."),
        py::arg("dx"),
        py::arg("dy"),
        py::arg("dz"));
    SelectionBox.def(
        "transform",
        &Amulet::SelectionBox::transform,
        py::arg("matrix"),
        py::doc("Transform this box by the given transformation matrix."));

    // Dunder methods
    SelectionBox.def(py::self < py::self);
    SelectionBox.def(py::self <= py::self);
    SelectionBox.def(py::self == py::self);
    SelectionBox.def(py::self >= py::self);
    SelectionBox.def(py::self > py::self);
    SelectionBox.def(
        "__repr__",
        [](const Amulet::SelectionBox& self) {
            return "SelectionBox("
                + std::to_string(self.min_x())
                + ", "
                + std::to_string(self.min_y())
                + ", "
                + std::to_string(self.min_z())
                + ", "
                + std::to_string(self.size_x())
                + ", "
                + std::to_string(self.size_y())
                + ", "
                + std::to_string(self.size_z())
                + ")";
        });
    SelectionBox.def(
        "__str__",
        [](const Amulet::SelectionBox& self) {
            return "("
                + std::to_string(self.min_x())
                + ", "
                + std::to_string(self.min_y())
                + ", "
                + std::to_string(self.min_z())
                + ", "
                + std::to_string(self.size_x())
                + ", "
                + std::to_string(self.size_y())
                + ", "
                + std::to_string(self.size_z())
                + ")";
        });
    SelectionBox.def(
        "__hash__",
        [](const Amulet::SelectionBox& self) {
            return py::hash(
                py::make_tuple(
                    self.min_x(),
                    self.min_y(),
                    self.min_z(),
                    self.size_x(),
                    self.size_y(),
                    self.size_z()));
        });
}
