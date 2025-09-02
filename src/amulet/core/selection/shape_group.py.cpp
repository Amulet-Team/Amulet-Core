#include <pybind11/pybind11.h>
#include <pybind11/typing.h>

#include <amulet/pybind11_extensions/collections.hpp>

#include "box_group.hpp"
#include "cuboid.hpp"
#include "shape_group.hpp"

namespace py = pybind11;
namespace pyext = Amulet::pybind11_extensions;

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
            [](const Amulet::SelectionBoxGroup& boxes) {
                std::vector<std::unique_ptr<const Amulet::SelectionShape>> shapes;
                for (const auto& box : boxes) {
                    shapes.push_back(std::make_unique<Amulet::SelectionCuboid>(box.min_x(), box.min_y(), box.min_z(), box.size_x(), box.size_y(), box.size_z()));
                }
                return Amulet::SelectionShapeGroup(std::move(shapes));
            }));
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
            ">>>     SelectionCuboid(0, 0, 0, 5, 5, 5),\n"
            ">>>     SelectionEllipsoid(7.5, 0, 0, 2.5)\n"
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

    SelectionShapeGroup.def(
        "voxelise",
        &Amulet::SelectionShapeGroup::voxelise,
        py::doc("Convert the shapes to a SelectionBoxGroup."));
    SelectionShapeGroup.def(
        "almost_equal",
        &Amulet::SelectionShapeGroup::almost_equal,
        py::arg("other"),
        py::doc("Returns True of the shape groups are equal or almost equal."));

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
