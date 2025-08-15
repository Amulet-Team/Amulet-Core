#include <pybind11/operators.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <concepts>
#include <ranges>
#include <type_traits>

#include <amulet/pybind11_extensions/collections.hpp>
#include <amulet/pybind11_extensions/py_module.hpp>

#include <amulet/core/selection/box.hpp>
#include <amulet/core/selection/box_group.hpp>
#include <amulet/core/selection/shape.hpp>
#include <amulet/core/selection/shape_group.hpp>
#include <amulet/core/selection/sphere.hpp>

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

static void init_selection_shape(py::classh<Amulet::SelectionShape> SelectionShape)
{
    SelectionShape.def(
        "voxelise",
        &Amulet::SelectionShape::voxelise,
        py::doc("Convert the shape into unit voxels.")
    );
}

static void init_selection_box(py::classh<Amulet::SelectionBox> SelectionBox)
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
        py::init<const Amulet::SelectionBox&>(),
        py::arg("box"),
        py::doc(
            "Create a SelectionBoxGroup containing the given box.\n"
            "\n"
            ">>> SelectionBoxGroup(SelectionBox(0, 0, 0, 1, 1, 1))"));
    static_assert(std::ranges::input_range<pyext::collections::Iterable<Amulet::SelectionBox>>);
    static_assert(std::convertible_to<std::ranges::range_value_t<pyext::collections::Iterable<Amulet::SelectionBox>>, const Amulet::SelectionBox&>);
    SelectionBoxGroup.def(
        py::init(
            [](pyext::collections::Iterable<Amulet::SelectionBox> boxes) {
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
        "selection_boxes",
        py::cpp_function(
            [](const Amulet::SelectionBoxGroup& self) {
                return py::make_iterator(self.selection_boxes().begin(), self.selection_boxes().end());
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
        py::arg("x"),
        py::arg("y"),
        py::arg("z"),
        py::doc(
            "Create a new :class:`SelectionBoxGroup` based on this one with the coordinates moved by the given offset.\n"
            "\n"
            ":param x: The x offset.\n"
            ":param y: The y offset.\n"
            ":param z: The z offset.\n"
            ":return: The new selection with the given offset."));

    // Dunder methods
    SelectionBoxGroup.def(
        "__repr__",
        [](const Amulet::SelectionBoxGroup& self) {
            std::string out = "SelectionBoxGroup([";
            bool comma = false;
            for (const auto& box : self.selection_boxes()) {
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
            for (const auto& box : self.selection_boxes()) {
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
            return py::make_iterator(self.selection_boxes());
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

void init_selection_shape_group(py::classh<Amulet::SelectionShapeGroup> SelectionShapeGroup)
{
    // Constructors
    SelectionShapeGroup.def(
        py::init<>(),
        py::doc(
            "Create an empty SelectionShapeGroup.\n"
            "\n"
            ">>> SelectionShapeGroup()"));
    SelectionShapeGroup.def(
        py::init<const Amulet::SelectionShape&>(),
        py::arg("selection"),
        py::doc(
            "Create a SelectionShapeGroup containing the given selection.\n"
            "\n"
            ">>> SelectionShapeGroup(SelectionShape(0, 0, 0, 1, 1, 1))"));
    SelectionShapeGroup.def(
        py::init(
            [](py::typing::Iterable<Amulet::SelectionShape> py_shapes) {
                std::vector<std::unique_ptr<const Amulet::SelectionShape>> shapes;
                for (const auto& py_shape : py_shapes) {
                    shapes.push_back(py_shape.cast<const Amulet::SelectionShape&>().copy());
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
}

static py::module init_selection_sphere(py::module m_parent)
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
    return m;
}

void init_selection(py::module m_parent)
{
    auto m = pyext::def_subpackage(m_parent, "selection");

    auto selection_shape_module = m.def_submodule("shape");
    auto selection_shape_group_module = m.def_submodule("shape_group");
    auto selection_box_module = m.def_submodule("box");
    auto selection_box_group_module = m.def_submodule("box_group");
    auto selection_group_module = m.def_submodule("group");

    py::classh<Amulet::SelectionShape> SelectionShape(selection_shape_module, "SelectionShape",
        "A base class for selection classes.");
    py::classh<Amulet::SelectionShapeGroup> SelectionShapeGroup(selection_shape_group_module, "SelectionShapeGroup",
        "A group of selection shapes.");
    py::classh<Amulet::SelectionBox, Amulet::SelectionShape> SelectionBox(selection_box_module, "SelectionBox",
        "The SelectionBox class represents a single cuboid selection.\n"
        "\n"
        "When combined with :class:`~amulet.api.selection.SelectionBoxGroup` it can represent any arbitrary shape.");
    py::classh<Amulet::SelectionBoxGroup> SelectionBoxGroup(selection_box_group_module, "SelectionBoxGroup",
        "A container for zero or more :class:`SelectionBox` instances.\n"
        "\n"
        "This allows for non-rectangular and non-contiguous selections.");

    init_selection_shape(SelectionShape);
    init_selection_shape_group(SelectionShapeGroup);
    init_selection_box(SelectionBox);
    init_selection_box_group(SelectionBoxGroup);

    m.attr("SelectionShape") = selection_shape_module.attr("SelectionShape");
    m.attr("SelectionShapeGroup") = selection_shape_group_module.attr("SelectionShapeGroup");
    m.attr("SelectionBox") = selection_box_module.attr("SelectionBox");
    m.attr("SelectionBoxGroup") = selection_box_group_module.attr("SelectionBoxGroup");
    // Backwards compatibility
    selection_group_module.attr("SelectionGroup") = selection_box_group_module.attr("SelectionBoxGroup");
    m.attr("SelectionGroup") = selection_group_module.attr("SelectionGroup");

    // Complex shapes
    m.attr("SelectionSphere") = init_selection_sphere(m).attr("SelectionSphere");
}
