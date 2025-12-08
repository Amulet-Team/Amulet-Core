#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <amulet/pybind11_extensions/builtins.hpp>
#include <amulet/pybind11_extensions/mapping.hpp>
#include <amulet/pybind11_extensions/mutable_mapping.hpp>

#include <amulet/core/version/version.hpp>

#include "block_entity_component.hpp"

namespace py = pybind11;
namespace pyext = Amulet::pybind11_extensions;

py::module init_block_entity_component(py::module m_parent)
{
    auto m = m_parent.def_submodule("block_entity_component");

    py::classh<Amulet::BlockEntityStorage>
        BlockEntityStorage(m, "BlockEntityStorage");
    BlockEntityStorage.def(
        py::init<
            const Amulet::VersionRange&,
            std::uint16_t,
            std::uint16_t>(),
        py::arg("version_range"),
        py::arg("x_size"),
        py::arg("z_size"));
    BlockEntityStorage.def_property_readonly(
        "x_size",
        &Amulet::BlockEntityStorage::get_x_size);
    BlockEntityStorage.def_property_readonly(
        "z_size",
        &Amulet::BlockEntityStorage::get_z_size);
    BlockEntityStorage.def(
        "__getitem__",
        [](const Amulet::BlockEntityStorage& self, const Amulet::BlockEntityChunkCoord& key) {
            try {
                return pybind11::cast(self.get(key));
            } catch (const std::out_of_range&) {
                throw pybind11::key_error(pybind11::repr(py::cast(key)));
            }
        });
    BlockEntityStorage.def(
        "__iter__",
        [](Amulet::BlockEntityStorage& self) {
            return pyext::make_map_iterator(self.get_block_entities());
        },
        pybind11::keep_alive<0, 1>());
    BlockEntityStorage.def(
        "__len__",
        &Amulet::BlockEntityStorage::get_size);
    BlockEntityStorage.def(
        "__contains__",
        &Amulet::BlockEntityStorage::contains);
    using Mapping = pyext::collections::MutableMapping<Amulet::BlockEntityChunkCoord, std::shared_ptr<Amulet::BlockEntity>>;
    Mapping::def_repr(BlockEntityStorage);
    Mapping::def_keys(BlockEntityStorage);
    Mapping::def_values(BlockEntityStorage);
    Mapping::def_items(BlockEntityStorage);
    Mapping::def_get(BlockEntityStorage);
    Mapping::def_eq(BlockEntityStorage);
    Mapping::def_hash(BlockEntityStorage);
    Mapping::register_cls(BlockEntityStorage);
    BlockEntityStorage.def(
        "__setitem__",
        [](
            Amulet::BlockEntityStorage& self,
            const Amulet::BlockEntityChunkCoord& key,
            pyext::PyObjectCpp<Amulet::BlockEntity> value) {
            std::shared_ptr<Amulet::BlockEntity> block_ptr;
            try {
                block_ptr = value.cast<std::shared_ptr<Amulet::BlockEntity>>();
            } catch (const std::runtime_error&) {
                block_ptr = std::make_shared<Amulet::BlockEntity>(value.cast<Amulet::BlockEntity&>());
            }
            self.set(key, block_ptr);
        },
        pybind11::arg("key"), pybind11::arg("value"));
    BlockEntityStorage.def(
        "__delitem__",
        &Amulet::BlockEntityStorage::del,
        pybind11::arg("key"));
    BlockEntityStorage.def(
        "clear",
        &Amulet::BlockEntityStorage::clear);
    Mapping::def_pop(BlockEntityStorage);
    Mapping::def_popitem(BlockEntityStorage);
    Mapping::def_update(BlockEntityStorage);
    Mapping::def_setdefault(BlockEntityStorage);
    Mapping::register_cls(BlockEntityStorage);

    py::classh<Amulet::BlockEntityComponent>
        BlockEntityComponent(m, "BlockEntityComponent");
    BlockEntityComponent.def_readonly_static(
        "ComponentID",
        &Amulet::BlockEntityComponent::ComponentID);
    BlockEntityComponent.def_property(
        "block_entity_storage",
        &Amulet::BlockEntityComponent::get_block_entity_storage,
        &Amulet::BlockEntityComponent::set_block_entity_storage);

    return m;
}
