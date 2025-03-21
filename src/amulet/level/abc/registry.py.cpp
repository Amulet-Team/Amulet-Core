#include <pybind11/pybind11.h>

#include <memory>

#include <pybind11_extensions/collections.hpp>

#include <amulet/collections/iterator.py.hpp>
#include <amulet/collections/mapping.py.hpp>

#include "registry.hpp"

namespace py = pybind11;

py::module init_registry(py::module m_parent)
{
    auto m = m_parent.def_submodule("registry");

    py::class_<Amulet::IdRegistry, std::shared_ptr<Amulet::IdRegistry>> IdRegistry(m, "IdRegistry",
        "A registry for namespaced ids.\n"
        "External synchronisation is required with this class.");
    IdRegistry.def(py::init<>());
    IdRegistry.def_property_readonly(
        "lock",
        &Amulet::IdRegistry::get_mutex,
        py::keep_alive<0, 1>(),
        py::doc("The public lock.\n"
                "Thread safe."));
    IdRegistry.def(
        "numerical_id_to_namespace_id",
        [](const Amulet::IdRegistry& self, std::uint32_t index) {
            try {
                return self.numerical_id_to_namespace_id(index);
            } catch (const std::out_of_range&) {
                throw py::key_error(std::to_string(index));
            }
        },
        py::arg("index"),
        py::doc("Convert a numerical id to its namespaced id.\n"
                "External shared lock required."));
    IdRegistry.def(
        "namespace_id_to_numerical_id",
        [](const Amulet::IdRegistry& self, const Amulet::NamespacedName& name) {
            try {
                return self.namespace_id_to_numerical_id(name);
            } catch (const std::out_of_range&) {
                throw py::key_error(name.first + ":" + name.second);
            }
        },
        py::arg("name"),
        py::doc("Convert a namespaced id to its numerical id.\n"
                "External shared lock required."));
    IdRegistry.def(
        "namespace_id_to_numerical_id",
        [](const Amulet::IdRegistry& self, std::string namespace_, std::string base_name) {
            try {
                return self.namespace_id_to_numerical_id({ namespace_, base_name });
            } catch (const std::out_of_range&) {
                throw py::key_error(namespace_ + ":" + base_name);
            }
        },
        py::arg("namespace"),
        py::arg("base_name"),
        py::doc("Convert a namespaced id to its numerical id.\n"
                "External shared lock required."));
    IdRegistry.def(
        "register_id",
        &Amulet::IdRegistry::register_id,
        py::arg("index"),
        py::arg("name"),
        py::doc("Convert a namespaced id to its numerical id.\n"
                "External unique lock required."));
    IdRegistry.def(
        "__len__",
        &Amulet::IdRegistry::size,
        py::doc(
            "The number of ids registered.\n"
            "External shared lock required."));
    IdRegistry.def(
        "__iter__",
        [](const Amulet::IdRegistry& self) -> pybind11_extensions::collections::abc::Iterator<std::uint32_t> {
            return Amulet::collections::make_map_iterator<
                std::map<std::uint32_t, Amulet::NamespacedName>>(
                self.ids());
        },
        py::keep_alive<0, 1>(),
        py::doc("An iterable of the numerical ids registered.\n"
                "External shared lock required."));
    IdRegistry.def(
        "__getitem__",
        [](const Amulet::IdRegistry& self, std::uint32_t index) {
            try {
                return self.numerical_id_to_namespace_id(index);
            } catch (const std::out_of_range&) {
                throw py::key_error(std::to_string(index));
            }
        },
        py::arg("index"),
        py::doc("Convert a numerical id to its namespaced id.\n"
                "External shared lock required."));
    IdRegistry.def(
        "__getitem__",
        [](const Amulet::IdRegistry& self, const Amulet::NamespacedName& name) {
            try {
                return self.namespace_id_to_numerical_id(name);
            } catch (const std::out_of_range&) {
                throw py::key_error(name.first + ":" + name.second);
            }
        },
        py::arg("name"),
        py::doc("Convert a namespaced id to its numerical id.\n"
                "External shared lock required."));

    Amulet::collections::PyMapping_contains<std::uint32_t>(IdRegistry);
    Amulet::collections::PyMapping_keys<std::uint32_t>(IdRegistry);
    Amulet::collections::PyMapping_values<Amulet::NamespacedName>(IdRegistry);
    Amulet::collections::PyMapping_items<std::uint32_t, Amulet::NamespacedName>(IdRegistry);
    Amulet::collections::PyMapping_get<std::uint32_t, Amulet::NamespacedName>(IdRegistry);
    Amulet::collections::PyMapping_eq(IdRegistry);
    Amulet::collections::PyMapping_hash(IdRegistry);
    Amulet::collections::PyMapping_register(IdRegistry);

    return m;
}
