#include <pybind11/chrono.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <memory>

#include <amulet/version.hpp>

#include "raw_level.hpp"

namespace py = pybind11;

py::module init_java_raw_level(py::module m_parent)
{
    auto m = m_parent.def_submodule("raw_level");

    py::class_<
        Amulet::JavaCreateArgsV1>
        JavaCreateArgsV1(m, "JavaCreateArgsV1");
    JavaCreateArgsV1.def(
        py::init<bool, std::string, Amulet::VersionNumber, std::string>(),
        py::arg("overwrite"),
        py::arg("path"),
        py::arg("version"),
        py::arg("level_name"));
    JavaCreateArgsV1.def_readonly(
        "overwrite",
        &Amulet::JavaCreateArgsV1::overwrite);
    JavaCreateArgsV1.def_property_readonly(
        "path",
        [](const Amulet::JavaCreateArgsV1& self) {
            return self.path.string();
        });
    JavaCreateArgsV1.def_readonly(
        "version",
        &Amulet::JavaCreateArgsV1::version);
    JavaCreateArgsV1.def_readonly(
        "level_name",
        &Amulet::JavaCreateArgsV1::level_name);

    py::class_<
        Amulet::JavaRawLevel,
        std::shared_ptr<Amulet::JavaRawLevel>>
        JavaRawLevel(m, "JavaRawLevel");
    JavaRawLevel.def_static(
        "load",
        [](const std::string& path) -> std::shared_ptr<Amulet::JavaRawLevel> {
            return Amulet::JavaRawLevel::load(path);
        },
        py::arg("path"),
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Load an existing Java level from the given directory.\n"
                "Thread safe."));
    JavaRawLevel.def_static(
        "create",
        [](const Amulet::JavaCreateArgsV1& args) -> std::shared_ptr<Amulet::JavaRawLevel> {
            return Amulet::JavaRawLevel::create(args);
        },
        py::arg("args"),
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Create a new Java level at the given directory.\n"
                "Thread safe."));
    JavaRawLevel.def(
        "lock",
        &Amulet::JavaRawLevel::get_mutex,
        py::doc("The public lock\n"
                "Thread safe."));
    JavaRawLevel.def(
        "is_open",
        &Amulet::JavaRawLevel::is_open,
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Is the level open.\n"
                "External shared read lock required."));
    JavaRawLevel.def(
        "reload_metadata",
        &Amulet::JavaRawLevel::reload_metadata,
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Reload the metadata. This can only be called when the level is closed.\n"
                "External unique lock required."));
    JavaRawLevel.def(
        "open",
        &Amulet::JavaRawLevel::open,
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Open the level.\n"
                "External unique lock required."));
    JavaRawLevel.def(
        "close",
        &Amulet::JavaRawLevel::close,
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Close the level.\n"
                "External unique lock required."));
    JavaRawLevel.def_property_readonly(
        "path",
        [](const Amulet::JavaRawLevel& self) {
            return self.get_path().string();
        },
        py::doc("The path to the level directory.\n"
                "Thread safe."));
    JavaRawLevel.def_property(
        "level_dat",
        &Amulet::JavaRawLevel::get_level_dat,
        &Amulet::JavaRawLevel::set_level_dat,
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Getter:\n"
                "The NamedTag stored in the level.dat file. Returns a unique copy.\n"
                "External shared read lock required.\n"
                "\n"
                "Setter:\n"
                "Set the level.dat NamedTag\n"
                "External unique lock required."));
    JavaRawLevel.def_property_readonly(
        "platform",
        &Amulet::JavaRawLevel::get_platform,
        py::doc("The platform identifier. \"java\"\n"
                "Thread safe."));
    JavaRawLevel.def_property(
        "data_version",
        &Amulet::JavaRawLevel::get_data_version,
        &Amulet::JavaRawLevel::set_data_version,
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Getter:\n"
                "The game data version that the level was last opened in.\n"
                "External shared read lock required.\n"
                "\n"
                "Setter:\n"
                "Set the maximum game version.\n"
                "If the game version is different this will close and re-open the level.\n"
                "External unique lock required."));
    JavaRawLevel.def_property_readonly(
        "modified_time",
        &Amulet::JavaRawLevel::get_modified_time,
        py::call_guard<py::gil_scoped_release>(),
        py::doc("The time when the level was lasted edited.\n"
                "External shared read lock required."));
    JavaRawLevel.def_property(
        "level_name",
        &Amulet::JavaRawLevel::get_level_name,
        &Amulet::JavaRawLevel::set_level_name,
        py::doc("Getter:\n"
                "The name of the level.\n"
                "External shared read lock required.\n"
                "\n"
                "Setter:\n"
                "Set the level name.\n"
                "External unique lock required."));
    JavaRawLevel.def_property_readonly(
        "dimension_ids",
        &Amulet::JavaRawLevel::get_dimension_ids,
        py::call_guard<py::gil_scoped_release>(),
        py::doc("The identifiers for all dimensions in this level.\n"
                "External shared read lock required.\n"
                "External shared read-only lock optional."));
    JavaRawLevel.def(
        "get_dimension",
        &Amulet::JavaRawLevel::get_dimension,
        py::arg("dimension_id"),
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Get the raw dimension object for a specific dimension.\n"
                "External shared read lock required."));
    JavaRawLevel.def(
        "compact",
        &Amulet::JavaRawLevel::compact,
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Compact the level.\n"
                "External shared read lock required."));
    JavaRawLevel.def(
        "get_block_id_override",
        &Amulet::JavaRawLevel::get_block_id_override,
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Overridden block ids.\n"
                "External shared read lock required."));
    JavaRawLevel.def(
        "get_biome_id_override",
        &Amulet::JavaRawLevel::get_biome_id_override,
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Overridden biome ids.\n"
                "External shared read lock required."));

    return m;
}
