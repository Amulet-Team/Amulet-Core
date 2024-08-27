#include <memory>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/operators.h>
#include <pybind11/typing.h>

#include <amulet_nbt/tag/named_tag.hpp>
#include <amulet/version.hpp>
#include <amulet/block_entity.hpp>


namespace py = pybind11;

void init_block_entity(py::module block_entity_module) {
    py::object NotImplemented = py::module::import("builtins").attr("NotImplemented");

    // Required for docstrings
    py::module::import("amulet_nbt");

    py::class_<Amulet::BlockEntity, Amulet::PlatformVersionContainer, std::shared_ptr<Amulet::BlockEntity>> BlockEntity(block_entity_module, "BlockEntity",
        "A class to contain all the data to define a BlockEntity."
    );
        BlockEntity.def(
            py::init<
                const Amulet::PlatformType&,
                std::shared_ptr<Amulet::VersionNumber>,
                const std::string&,
                const std::string&,
                std::shared_ptr<AmuletNBT::NamedTag>
            >(),
            py::arg("platform"),
            py::arg("version"),
            py::arg("namespace"),
            py::arg("base_name"),
            py::arg("nbt")
        );
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
                ":return: The namespace:base_name of the block entity"
            )
        );
        BlockEntity.def_property(
            "namespace",
            &Amulet::BlockEntity::get_namespace,
            &Amulet::BlockEntity::set_namespace,
            py::doc(
                "The namespace of the block entity represented by the :class:`BlockEntity` object.\n"
                "\n"
                ">>> block_entity: BlockEntity\n"
                ">>> block_entity.namespace\n"
                "\n"
                ":return: The namespace of the block entity"
            )
        );
        BlockEntity.def_property(
            "base_name",
            &Amulet::BlockEntity::get_base_name,
            &Amulet::BlockEntity::set_base_name,
            py::doc(
                "The base name of the block entity represented by the :class:`BlockEntity` object.\n"
                "\n"
                ">>> block_entity: BlockEntity\n"
                ">>> block_entity.base_name\n"
                "\n"
                ":return: The base name of the block entity"
            )
        );
        BlockEntity.def_property(
            "nbt",
            &Amulet::BlockEntity::get_nbt,
            &Amulet::BlockEntity::set_nbt,
            py::doc(
                "The nbt data for the block entity.\n"
                ">>> block_entity: BlockEntity\n"
                ">>> block_entity.nbt\n"
                "\n"
                ":return: The NamedTag of the block entity"
            )
        );
        BlockEntity.def(
            "__repr__",
            [](const Amulet::BlockEntity& self){
                return "Block(" +
                    py::repr(py::cast(self.get_platform())).cast<std::string>() + ", " +
                    py::repr(py::cast(self.get_version())).cast<std::string>() + ", " +
                    py::repr(py::cast(self.get_namespace())).cast<std::string>() + ", " +
                    py::repr(py::cast(self.get_base_name())).cast<std::string>() + ", " +
                    py::repr(py::cast(self.get_nbt())).cast<std::string>() +
                ")";
            }
        );
        BlockEntity.def(
            py::pickle(
                [](const Amulet::BlockEntity& self) -> py::bytes {
                    return py::bytes(Amulet::serialise(self));
                },
                [](py::bytes state){
                    return Amulet::deserialise<Amulet::BlockEntity>(state.cast<std::string>());
                }
            )
        );

        BlockEntity.def(
            "__eq__",
            [NotImplemented](const Amulet::BlockEntity& self, py::object other) -> py::object {
                if (py::isinstance<Amulet::BlockEntity>(other)) {
                    return py::cast(self == other.cast<Amulet::BlockEntity>());
                }
                return NotImplemented;
            },
            py::is_operator()
        );
        BlockEntity.def(
            "__ne__",
            [NotImplemented](const Amulet::BlockEntity& self, py::object other) -> py::object {
                if (py::isinstance<Amulet::BlockEntity>(other)) {
                    return py::cast(self != other.cast<Amulet::BlockEntity>());
                }
                return NotImplemented;
            },
            py::is_operator()
        );
}
