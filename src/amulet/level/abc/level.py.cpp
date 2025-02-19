#include <pybind11/chrono.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <memory>

#include <pybind11_extensions/py_module.hpp>

#include <amulet/utils/signal.py.hpp>

#include "level.hpp"

namespace py = pybind11;

py::module init_level_abc_level(py::module m_parent)
{
    auto m = m_parent.def_submodule("level");

    py::class_<Amulet::LevelMetadata, std::shared_ptr<Amulet::LevelMetadata>> LevelMetadata(m, "LevelMetadata");
    LevelMetadata.def(
        "is_open",
        &Amulet::LevelMetadata::is_open,
        py::doc(
            "Has the level been opened.\n"
            "\n"
            ":return: True if the level is open otherwise False."));
    LevelMetadata.def_property_readonly(
        "platform",
        &Amulet::LevelMetadata::get_platform,
        py::doc("The platform string for the level.\n"
                "External shared read lock required."));
    LevelMetadata.def_property_readonly(
        "max_game_version",
        &Amulet::LevelMetadata::get_max_game_version,
        py::doc("The maximum game version the level has been opened with.\n"
                "External shared read lock required."));
    LevelMetadata.def_property_readonly(
        "level_name",
        &Amulet::LevelMetadata::get_level_name,
        py::doc("The name of the level\n"
                "External shared read lock required."));
    LevelMetadata.def_property_readonly(
        "modified_time",
        &Amulet::LevelMetadata::get_modified_time,
        py::doc("The time when the level was last modified.\n"
                "External shared read lock required."));
    LevelMetadata.def_property_readonly(
        "sub_chunk_size",
        &Amulet::LevelMetadata::get_sub_chunk_size,
        py::doc("The size of the sub-chunk. Must be a cube.\n"
                "External shared read lock required."));
    LevelMetadata.def_property_readonly(
        "lock",
        &Amulet::LevelMetadata::get_mutex,
        py::doc("The external mutex for the level.\n"
                "Thread safe."));

    py::class_<
        Amulet::Level,
        std::shared_ptr<Amulet::Level>,
        Amulet::LevelMetadata>
        Level(m, "Level");
    Amulet::def_signal(
        Level,
        "opened",
        &Amulet::Level::opened,
        py::doc("Signal emitted when the level is opened.\n"
                "Thread safe."));
    Level.def(
        "open",
        &Amulet::Level::open,
        py::doc("Open the level.\n"
                "\n"
                "If the level is already open, this does nothing.\n"
                "External unique lock required.\n"
                "\n"
                ":raises amulet.utils.task_manager.TaskCancelled: If the task is cancelled."));
    // Amulet::def_signal(
    //     Level,
    //     "purged",
    //     &Amulet::Level::purged,
    //     py::doc("Signal emitted when the level is purged\n"
    //             "Thread safe."));
    //  Level.def(
    //      "purge",
    //      &Amulet::Level::purge,
    //      py::doc("Clear all unsaved changes.\n"
    //              "External unique lock required."));
    Level.def(
        "save",
        &Amulet::Level::save,
        py::doc("Save all changes to the level.\n"
                "External unique lock required."));
    Amulet::def_signal(
        Level,
        "closed",
        &Amulet::Level::closed,
        py::doc("Signal emitted when the level is closed.\n"
                "Thread safe."));
    Level.def(
        "close",
        &Amulet::Level::close,
        py::doc("Close the level.\n"
                "\n"
                "If the level is not open, this does nothing.\n"
                "\n"
                ":raises amulet.utils.task_manager.TaskCancelled: If the task is cancelled."));
    Level.def(
        "dimension_ids",
        &Amulet::Level::get_dimension_ids,
        py::doc("The identifiers for all dimensions in the level.\n"
                "External shared read lock required."));
    Level.def(
        "get_dimension",
        &Amulet::Level::get_dimension,
        py::arg("dimension_id"),
        py::doc("Get a dimension.\n"
                "External shared read lock required."));

    py::class_<Amulet::CompactibleLevel, std::shared_ptr<Amulet::CompactibleLevel>> CompactibleLevel(m, "CompactibleLevel");
    CompactibleLevel.def(
        "compact",
        &Amulet::CompactibleLevel::compact,
        py::doc("Compact the level data to reduce file size.\n"
                "External unique lock required."));

    py::class_<Amulet::DiskLevel, std::shared_ptr<Amulet::DiskLevel>> DiskLevel(m, "DiskLevel");
    DiskLevel.def(
        "path",
        [](Amulet::DiskLevel& self) { return self.get_path().string(); },
        py::doc("The path to the level on disk.\n"
                "External shared read lock required."));

    py::class_<Amulet::ReloadableLevel, std::shared_ptr<Amulet::ReloadableLevel>> ReloadableLevel(m, "ReloadableLevel");
    ReloadableLevel.def(
        "reload_metadata",
        &Amulet::ReloadableLevel::reload_metadata,
        py::doc("Reload the level metadata.\n"
                "This can only be done when the level is not open.\n"
                "External unique mutex required."));
    Amulet::def_signal(
        ReloadableLevel,
        "reloaded",
        &Amulet::ReloadableLevel::reloaded,
        py::doc("Signal emitted when the level is reloaded.\n"
                "Thread safe."));
    ReloadableLevel.def(
        "reload",
        &Amulet::ReloadableLevel::reload,
        py::doc("Reload the level.\n"
                "This is like closing and opening the level but does not release locks.\n"
                "This can only be done when the level is open."
                "External unique mutex required."));

    return m;
}
