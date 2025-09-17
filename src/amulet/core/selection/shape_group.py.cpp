#include <pybind11/operators.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/typing.h>

#include <algorithm>
#include <functional>
#include <variant>

#include <amulet/pybind11_extensions/builtins.hpp>
#include <amulet/pybind11_extensions/collections.hpp>
#include <amulet/pybind11_extensions/mutable_sequence.hpp>

#include "box_group.hpp"
#include "cuboid.hpp"
#include "shape_group.hpp"

namespace py = pybind11;
namespace pyext = Amulet::pybind11_extensions;

size_t sanitise_index(size_t size, Py_ssize_t index)
{
    if (index < 0) {
        index += size;
        if (index < 0) {
            throw py::index_error();
        }
    } else if (size <= index) {
        throw py::index_error();
    }
    return index;
}

inline std::shared_ptr<Amulet::SelectionShape> get_shape(py::handle obj)
{
    try {
        return obj.cast<std::shared_ptr<Amulet::SelectionShape>>();
    } catch (const std::runtime_error&) {
        return obj.cast<const Amulet::SelectionShape&>().copy();
    }
}

void init_selection_shape_group(py::module m, py::classh<Amulet::SelectionShapeGroup> SelectionShapeGroup)
{
    std::string module_name = m.attr("__name__").cast<std::string>();

    // Constructors
    SelectionShapeGroup.def(
        py::init<>(),
        py::doc(
            "Create an empty SelectionShapeGroup.\n"
            "\n"
            ">>> SelectionShapeGroup()"));
    SelectionShapeGroup.def(
        py::init(
            [](const Amulet::SelectionBoxGroup& box_group) {
                std::vector<std::shared_ptr<Amulet::SelectionShape>> shapes;
                for (const auto& box : box_group) {
                    shapes.push_back(std::make_shared<Amulet::SelectionCuboid>(
                        static_cast<double>(box.min_x()),
                        static_cast<double>(box.min_y()),
                        static_cast<double>(box.min_z()),
                        static_cast<double>(box.size_x()),
                        static_cast<double>(box.size_y()),
                        static_cast<double>(box.size_z())));
                }
                return Amulet::SelectionShapeGroup(std::move(shapes));
            }),
        py::arg("box_group"));
    SelectionShapeGroup.def(
        py::init(
            [](py::typing::Iterable<Amulet::SelectionShape> py_shapes) {
                std::vector<std::shared_ptr<Amulet::SelectionShape>> shapes;
                for (const auto& shape : py_shapes) {
                    shapes.push_back(get_shape(shape));
                }
                return Amulet::SelectionShapeGroup(std::move(shapes));
            }),
        py::arg("shapes"),
        py::doc(
            "Create a SelectionShapeGroup from the selections in the iterable.\n"
            "\n"
            ">>> SelectionShapeGroup([\n"
            ">>>     SelectionCuboid(0, 0, 0, 5, 5, 5),\n"
            ">>>     SelectionEllipsoid(7.5, 0, 0, 2.5)\n"
            ">>> ])\n"));
    SelectionShapeGroup.def(
        "__copy__",
        [](const Amulet::SelectionShapeGroup& self) {
            return self;
        });
    SelectionShapeGroup.def(
        "__deepcopy__",
        [](const Amulet::SelectionShapeGroup& self, py::dict) {
            return self.deep_copy();
        },
        py::arg("memo"));

    SelectionShapeGroup.def(
        "serialise",
        &Amulet::SelectionShapeGroup::serialise);

    SelectionShapeGroup.def_static(
        "deserialise",
        &Amulet::SelectionShapeGroup::deserialise,
        py::arg("s"));

    SelectionShapeGroup.def(
        "voxelise",
        &Amulet::SelectionShapeGroup::voxelise,
        py::doc("Convert the shapes to a SelectionBoxGroup."));
    SelectionShapeGroup.def(
        "almost_equal",
        &Amulet::SelectionShapeGroup::almost_equal,
        py::arg("other"),
        py::doc("Returns True of the shape groups are equal or almost equal."));
    SelectionShapeGroup.def(py::self == py::self);

    // Sequence
    SelectionShapeGroup.def(
        "__getitem__",
        [](const Amulet::SelectionShapeGroup& self, Py_ssize_t index) {
            return self.get_shapes()[sanitise_index(self.count(), index)];
        },
        py::arg("index"));
    SelectionShapeGroup.def(
        "__bool__",
        &Amulet::SelectionShapeGroup::operator bool,
        py::doc("Are there any selections in the group."));
    SelectionShapeGroup.def(
        "__len__",
        &Amulet::SelectionShapeGroup::count,
        py::doc("The number of :class:`SelectionShape` classes in the group."));

    // MutableSequence
    SelectionShapeGroup.def(
        "__setitem__",
        [](
            Amulet::SelectionShapeGroup& self,
            Py_ssize_t index,
            pyext::PyObjectCpp<Amulet::SelectionShape> item) {
            self.get_shapes()[sanitise_index(self.count(), index)] = get_shape(item);
        },
        py::arg("index"),
        py::arg("item"));
    SelectionShapeGroup.def(
        "__delitem__",
        [](Amulet::SelectionShapeGroup& self, Py_ssize_t index) {
            self.get_shapes().erase(self.get_shapes().begin() + sanitise_index(self.count(), index));
        },
        py::arg("index"));
    SelectionShapeGroup.def(
        "insert",
        [](
            Amulet::SelectionShapeGroup& self,
            Py_ssize_t index,
            pyext::PyObjectCpp<Amulet::SelectionShape> item) {
            if (index < 0) {
                index += self.count();
            }
            index = std::max(static_cast<Py_ssize_t>(0), std::min(static_cast<Py_ssize_t>(self.count()), index));
            self.get_shapes().insert(
                self.get_shapes().begin() + index,
                get_shape(item));
        },
        py::arg("index"),
        py::arg("item"));

    using ShapeSequence = pyext::collections::MutableSequence<Amulet::SelectionShape>;
    ShapeSequence::def_getitem_slice(SelectionShapeGroup);
    ShapeSequence::def_contains(SelectionShapeGroup);
    ShapeSequence::def_iter(SelectionShapeGroup);
    ShapeSequence::def_reversed(SelectionShapeGroup);
    ShapeSequence::def_index(SelectionShapeGroup);
    ShapeSequence::def_count(SelectionShapeGroup);
    ShapeSequence::def_append(SelectionShapeGroup);
    ShapeSequence::def_clear(SelectionShapeGroup);
    ShapeSequence::def_reverse(SelectionShapeGroup);
    ShapeSequence::def_extend(SelectionShapeGroup);
    ShapeSequence::def_pop(SelectionShapeGroup);
    ShapeSequence::def_remove(SelectionShapeGroup);
    ShapeSequence::def_iadd(SelectionShapeGroup);
    ShapeSequence::register_cls(SelectionShapeGroup);

    auto repr = py::module::import("builtins").attr("repr");
    SelectionShapeGroup.def(
        "__repr__",
        [module_name, repr](const Amulet::SelectionShapeGroup& self) {
            std::string s = module_name + ".SelectionShapeGroup([";
            bool is_first = true;
            for (const auto& shape : self) {
                if (is_first) {
                    is_first = false;
                } else {
                    s += ", ";
                }
                s += repr(py::cast(*shape, py::return_value_policy::reference)).cast<std::string>();
            }
            s += "])";
            return s;
        });
}
