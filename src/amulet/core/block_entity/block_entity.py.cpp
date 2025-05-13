#include <pybind11/operators.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/typing.h>

#include <memory>

#include <amulet/pybind11_extensions/builtins.hpp>
#include <amulet/pybind11_extensions/hash.hpp>
#include <amulet/pybind11_extensions/py_module.hpp>

#include <amulet/nbt/tag/named_tag.hpp>

#include <amulet/core/version/version.hpp>

#include "block_entity.hpp"

namespace py = pybind11;
namespace pyext = Amulet::pybind11_extensions;

void init_block_entity(py::module m_parent)
{
    auto m = pyext::def_subpackage(m_parent, "block_entity");

    py::class_<Amulet::BlockEntity, Amulet::PlatformVersionContainer, std::shared_ptr<Amulet::BlockEntity>> BlockEntity(m, "BlockEntity",
        "A class to contain all the data to define a BlockEntity.");
    BlockEntity.def(
        py::init<
            const Amulet::PlatformType&,
            const Amulet::VersionNumber&,
            const std::string&,
            const std::string&,
            std::shared_ptr<Amulet::NBT::NamedTag>>(),
        py::arg("platform"),
        py::arg("version"),
        py::arg("namespace"),
        py::arg("base_name"),
        py::arg("nbt"));
    BlockEntity.def_property_readonly(
        "namespaced_name",
        [](const Amulet::BlockEntity& self) {
            return self.get_namespace() + ":" + self.get_base_name();
        },
        py::doc(
            "The namespace:base_name of the block entity represented by the :class:`BlockEntity` object.\n"
            "\n"
            ">>> block_entity: BlockEntity\n"
            ">>> block_entity.namespaced_name\n"
            "\n"
            ":return: The namespace:base_name of the block entity"));
    BlockEntity.def_property(
        "namespace",
        &Amulet::BlockEntity::get_namespace,
        &Amulet::BlockEntity::set_namespace<std::string>,
        py::doc(
            "The namespace of the block entity represented by the :class:`BlockEntity` object.\n"
            "\n"
            ">>> block_entity: BlockEntity\n"
            ">>> block_entity.namespace\n"
            "\n"
            ":return: The namespace of the block entity"));
    BlockEntity.def_property(
        "base_name",
        &Amulet::BlockEntity::get_base_name,
        &Amulet::BlockEntity::set_base_name<std::string>,
        py::doc(
            "The base name of the block entity represented by the :class:`BlockEntity` object.\n"
            "\n"
            ">>> block_entity: BlockEntity\n"
            ">>> block_entity.base_name\n"
            "\n"
            ":return: The base name of the block entity"));
    BlockEntity.def_property(
        "nbt",
        &Amulet::BlockEntity::get_nbt,
        [](Amulet::BlockEntity& self, pyext::PyObjectCpp<Amulet::NBT::NamedTag> tag) {
            std::shared_ptr<Amulet::NBT::NamedTag> tag_ptr;
            try {
                tag_ptr = tag.cast<std::shared_ptr<Amulet::NBT::NamedTag>>();
            } catch (const std::runtime_error&) {
                tag_ptr = std::make_shared<Amulet::NBT::NamedTag>(tag.cast<Amulet::NBT::NamedTag&>());
            }
            self.set_nbt(std::move(tag_ptr));
        },
        py::doc(
            "The nbt data for the block entity.\n"
            ">>> block_entity: BlockEntity\n"
            ">>> block_entity.nbt\n"
            "\n"
            ":return: The NamedTag of the block entity"));
    BlockEntity.def(
        "__repr__",
        [](const Amulet::BlockEntity& self) {
            return "BlockEntity("
                + py::repr(py::cast(self.get_platform())).cast<std::string>() + ", "
                + py::repr(py::cast(self.get_version(), py::return_value_policy::reference)).cast<std::string>() + ", "
                + py::repr(py::cast(self.get_namespace())).cast<std::string>() + ", "
                + py::repr(py::cast(self.get_base_name())).cast<std::string>() + ", "
                + py::repr(py::cast(self.get_nbt())).cast<std::string>() + ")";
        });
    BlockEntity.def(
        py::pickle(
            [](const Amulet::BlockEntity& self) -> py::bytes {
                return py::bytes(Amulet::serialise(self));
            },
            [](py::bytes state) {
                return Amulet::deserialise<Amulet::BlockEntity>(state.cast<std::string>());
            }));

    BlockEntity.def(py::self == py::self);
    pyext::def_hash_identity(BlockEntity);
}
