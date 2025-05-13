#include <pybind11/operators.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/typing.h>

#include <memory>

#include <amulet/pybind11_extensions/builtins.hpp>
#include <amulet/pybind11_extensions/hash.hpp>
#include <amulet/pybind11_extensions/py_module.hpp>

#include <amulet/nbt/tag/named_tag.hpp>

#include <amulet/core/entity/entity.hpp>
#include <amulet/core/version/version.hpp>

namespace py = pybind11;
namespace pyext = Amulet::pybind11_extensions;

void init_entity(py::module m_parent)
{
    auto m = pyext::def_subpackage(m_parent, "entity");

    py::class_<Amulet::Entity, Amulet::PlatformVersionContainer, std::shared_ptr<Amulet::Entity>> Entity(m, "Entity",
        "A class to contain all the data to define an Entity.");
    Entity.def(
        py::init<
            Amulet::PlatformType,
            Amulet::VersionNumber,
            std::string,
            std::string,
            double,
            double,
            double,
            std::shared_ptr<Amulet::NBT::NamedTag>>(),
        py::arg("platform"),
        py::arg("version"),
        py::arg("namespace"),
        py::arg("base_name"),
        py::arg("x"),
        py::arg("y"),
        py::arg("z"),
        py::arg("nbt"));
    Entity.def_property_readonly(
        "namespaced_name",
        [](const Amulet::Entity& self) {
            return self.get_namespace() + ":" + self.get_base_name();
        },
        py::doc(
            "The namespace:base_name of the entity represented by the :class:`Entity` object.\n"
            "\n"
            ">>> entity: Entity\n"
            ">>> entity.namespaced_name\n"
            "\n"
            ":return: The namespace:base_name of the entity"));
    Entity.def_property(
        "namespace",
        &Amulet::Entity::get_namespace,
        &Amulet::Entity::set_namespace<std::string&>,
        py::doc(
            "The namespace of the entity represented by the :class:`Entity` object.\n"
            "\n"
            ">>> entity: Entity\n"
            ">>> entity.namespace\n"
            "\n"
            ":return: The namespace of the entity"));
    Entity.def_property(
        "base_name",
        &Amulet::Entity::get_base_name,
        &Amulet::Entity::set_base_name<std::string&>,
        py::doc(
            "The base name of the entity represented by the :class:`Entity` object.\n"
            "\n"
            ">>> entity: Entity\n"
            ">>> entity.base_name\n"
            "\n"
            ":return: The base name of the entity"));
    Entity.def_property(
        "x",
        &Amulet::Entity::get_x,
        &Amulet::Entity::set_x,
        py::doc("The x coordinate of the entity."));
    Entity.def_property(
        "y",
        &Amulet::Entity::get_y,
        &Amulet::Entity::set_y,
        py::doc("The y coordinate of the entity."));
    Entity.def_property(
        "z",
        &Amulet::Entity::get_z,
        &Amulet::Entity::set_z,
        py::doc("The z coordinate of the entity."));
    Entity.def_property(
        "nbt",
        &Amulet::Entity::get_nbt,
        [](Amulet::Entity& self, pyext::PyObjectCpp<Amulet::NBT::NamedTag> tag) {
            std::shared_ptr<Amulet::NBT::NamedTag> tag_ptr;
            try {
                tag_ptr = tag.cast<std::shared_ptr<Amulet::NBT::NamedTag>>();
            } catch (const std::runtime_error&) {
                tag_ptr = std::make_shared<Amulet::NBT::NamedTag>(tag.cast<Amulet::NBT::NamedTag&>());
            }
            self.set_nbt(std::move(tag_ptr));
        },
        py::doc(
            "The nbt data for the entity.\n"
            ">>> entity: Entity\n"
            ">>> entity.nbt\n"
            "\n"
            ":return: The NamedTag of the entity"));
    Entity.def(
        "__repr__",
        [](const Amulet::Entity& self) {
            return "Entity("
                + py::repr(py::cast(self.get_platform())).cast<std::string>() + ", "
                + py::repr(py::cast(self.get_version(), py::return_value_policy::reference)).cast<std::string>() + ", "
                + py::repr(py::cast(self.get_namespace())).cast<std::string>() + ", "
                + py::repr(py::cast(self.get_base_name())).cast<std::string>() + ", "
                + std::to_string(self.get_x()) + ", "
                + std::to_string(self.get_y()) + ", "
                + std::to_string(self.get_z()) + ", "
                + py::repr(py::cast(self.get_nbt())).cast<std::string>() + ")";
        });
    Entity.def(
        py::pickle(
            [](const Amulet::Entity& self) -> py::bytes {
                return py::bytes(Amulet::serialise(self));
            },
            [](py::bytes state) {
                return Amulet::deserialise<Amulet::Entity>(state.cast<std::string>());
            }));

    Entity.def(py::self == py::self);
    pyext::def_hash_identity(Entity);
}
