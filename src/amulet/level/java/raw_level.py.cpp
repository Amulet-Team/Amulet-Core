#include <pybind11/chrono.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <memory>

#include <amulet/utils/holder.py.hpp>
#include <amulet/utils/signal.py.hpp>
#include <amulet/version/version.hpp>

#include "raw_level.hpp"

namespace py = pybind11;

py::module init_java_raw_level(py::module m_parent)
{
    auto m = m_parent.def_submodule("raw_level");

    py::class_<
        Amulet::JavaCreateArgsV1>
        JavaCreateArgsV1(m, "JavaCreateArgsV1");
    JavaCreateArgsV1.def(
        py::init<bool, const std::string&, const Amulet::VersionNumber&, const std::string&>(),
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
        Amulet::nogil_shared_ptr<Amulet::JavaRawLevel>>
        JavaRawLevel(m, "JavaRawLevel");
    JavaRawLevel.def_static(
        "load",
        [](const std::string& path) -> Amulet::nogil_shared_ptr<Amulet::JavaRawLevel> {
            return Amulet::JavaRawLevel::load(path);
        },
        py::arg("path"),
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Load an existing Java level from the given directory.\n"
                "Thread safe."));
    JavaRawLevel.def_static(
        "create",
        [](const Amulet::JavaCreateArgsV1& args) -> Amulet::nogil_shared_ptr<Amulet::JavaRawLevel> {
            return Amulet::JavaRawLevel::create(args);
        },
        py::arg("args"),
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Create a new Java level at the given directory.\n"
                "Thread safe."));
    JavaRawLevel.def_property_readonly(
        "lock",
        &Amulet::JavaRawLevel::get_mutex,
        py::keep_alive<0, 1>(),
        py::doc("The public lock\n"
                "Thread safe."));
    JavaRawLevel.def(
        "is_open",
        &Amulet::JavaRawLevel::is_open,
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Is the level open.\n"
                "External Read:SharedReadWrite lock required."));
    JavaRawLevel.def(
        "reload_metadata",
        &Amulet::JavaRawLevel::reload_metadata,
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Reload the metadata. This can only be called when the level is closed.\n"
                "External ReadWrite:Unique lock required."));
    Amulet::def_signal(
        JavaRawLevel,
        "opened",
        &Amulet::JavaRawLevel::opened);
    JavaRawLevel.def(
        "open",
        &Amulet::JavaRawLevel::open,
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Open the level.\n"
                "opened signal will be emitted when complete.\n"
                "External ReadWrite:Unique lock required."));
    Amulet::def_signal(
        JavaRawLevel,
        "closed",
        &Amulet::JavaRawLevel::closed);
    JavaRawLevel.def(
        "close",
        &Amulet::JavaRawLevel::close,
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Close the level.\n"
                "closed signal will be emitted when complete.\n"
                "External ReadWrite:Unique lock required."));
    Amulet::def_signal(
        JavaRawLevel,
        "reloaded",
        &Amulet::JavaRawLevel::reloaded);
    JavaRawLevel.def(
        "reload",
        &Amulet::JavaRawLevel::reload,
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Reload the level.\n"
                "This is like closing and re-opening without releasing the session.lock file.\n"
                "External ReadWrite:Unique lock required."));
    JavaRawLevel.def_property_readonly(
        "path",
        [](const Amulet::JavaRawLevel& self) {
            return self.get_path().string();
        },
        py::doc("The path to the level directory.\n"
                "Thread safe."));
    JavaRawLevel.def_property(
        "level_dat",
        py::cpp_function(
            &Amulet::JavaRawLevel::get_level_dat,
            py::call_guard<py::gil_scoped_release>()),
        py::cpp_function(
            &Amulet::JavaRawLevel::set_level_dat,
            py::call_guard<py::gil_scoped_release>()),
        py::doc("Getter:\n"
                "The NamedTag stored in the level.dat file. Returns a unique copy.\n"
                "External Read:SharedReadWrite lock required.\n"
                "\n"
                "Setter:\n"
                "Set the level.dat NamedTag\n"
                "This calls :meth:`reload` if the data version changed.\n"
                "External ReadWrite:Unique lock required."));
    JavaRawLevel.def_property_readonly(
        "platform",
        &Amulet::JavaRawLevel::get_platform,
        py::doc("The platform identifier. \"java\"\n"
                "Thread safe."));
    JavaRawLevel.def_property(
        "data_version",
        &Amulet::JavaRawLevel::get_data_version,
        py::cpp_function(
            &Amulet::JavaRawLevel::set_data_version,
            py::call_guard<py::gil_scoped_release>()),
        py::doc("Getter:\n"
                "The game data version that the level was last opened in.\n"
                "External Read:SharedReadWrite lock required.\n"
                "\n"
                "Setter:\n"
                "Set the maximum game version.\n"
                "If the game version is different this will call :meth:`reload`.\n"
                "External ReadWrite:SharedReadWrite lock required."));
    JavaRawLevel.def(
        "is_supported",
        &Amulet::JavaRawLevel::is_supported,
        py::doc(
            "Is this level a supported version.\n"
            "This is true for all versions we support and false for snapshots and unsupported newer versions.\n"
            "TODO: thread safety"));
    JavaRawLevel.def_property_readonly(
        "thumbnail",
        &Amulet::JavaRawLevel::get_thumbnail,
        py::doc("Get the thumbnail for the level.\n"
                "Thread safe."));
    JavaRawLevel.def_property_readonly(
        "modified_time",
        py::cpp_function(
            &Amulet::JavaRawLevel::get_modified_time,
            py::call_guard<py::gil_scoped_release>()),
        py::doc("The time when the level was lasted edited.\n"
                "External Read:SharedReadWrite lock required."));
    JavaRawLevel.def_property(
        "level_name",
        py::cpp_function(
            &Amulet::JavaRawLevel::get_level_name,
            py::call_guard<py::gil_scoped_release>()),
        py::cpp_function(
            &Amulet::JavaRawLevel::set_level_name,
            py::call_guard<py::gil_scoped_release>()),
        py::doc("Getter:\n"
                "The name of the level.\n"
                "External Read:SharedReadWrite lock required.\n"
                "\n"
                "Setter:\n"
                "Set the level name.\n"
                "External ReadWrite:Unique lock required."));
    JavaRawLevel.def_property_readonly(
        "dimension_ids",
        py::cpp_function(
            &Amulet::JavaRawLevel::get_dimension_ids,
            py::call_guard<py::gil_scoped_release>()),
        py::doc("The identifiers for all dimensions in this level.\n"
                "External Read:SharedReadWrite lock required.\n"
                "External Read:SharedReadOnly lock optional."));
    JavaRawLevel.def(
        "get_dimension",
        &Amulet::JavaRawLevel::get_dimension,
        py::arg("dimension_id"),
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Get the raw dimension object for a specific dimension.\n"
                "External Read:SharedReadWrite lock required."));
    JavaRawLevel.def(
        "compact",
        &Amulet::JavaRawLevel::compact,
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Compact the level.\n"
                "External Read:SharedReadWrite lock required."));
    JavaRawLevel.def_property_readonly(
        "block_id_override",
        &Amulet::JavaRawLevel::get_block_id_override,
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Overridden block ids.\n"
                "External Read:SharedReadWrite lock required."));
    JavaRawLevel.def_property_readonly(
        "biome_id_override",
        &Amulet::JavaRawLevel::get_biome_id_override,
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Overridden biome ids.\n"
                "External Read:SharedReadWrite lock required."));

    return m;
}
