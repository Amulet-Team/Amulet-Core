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
    LevelMetadata.def_property_readonly(
        "lock",
        &Amulet::LevelMetadata::get_mutex,
        py::keep_alive<0, 1>(),
        py::doc("The external mutex for the level.\n"
                "Thread safe."));
    LevelMetadata.def(
        "is_open",
        &Amulet::LevelMetadata::is_open,
        py::doc(
            "Has the level been opened.\n"
            "External Read:SharedReadWrite lock required.\n"
            "\n"
            ":return: True if the level is open otherwise False."));
    LevelMetadata.def_property_readonly(
        "platform",
        &Amulet::LevelMetadata::get_platform,
        py::doc("The platform string for the level.\n"
                "External Read:SharedReadWrite lock required."));
    LevelMetadata.def_property_readonly(
        "max_game_version",
        &Amulet::LevelMetadata::get_max_game_version,
        py::call_guard<py::gil_scoped_release>(),
        py::doc("The maximum game version the level has been opened with.\n"
                "External Read:SharedReadWrite lock required."));
    LevelMetadata.def(
        "is_supported",
        &Amulet::LevelMetadata::is_supported,
        py::doc("Is this level a supported version.\n"
                "This is true for all versions we support and false for snapshots, betas and unsupported newer versions.\n"
                "External Read:SharedReadWrite lock required."));
    LevelMetadata.def_property_readonly(
        "thumbnail",
        &Amulet::LevelMetadata::get_thumbnail,
        py::doc("The thumbnail for the level.\n"
                "External Read:SharedReadWrite lock required."));
    LevelMetadata.def_property_readonly(
        "level_name",
        &Amulet::LevelMetadata::get_level_name,
        py::call_guard<py::gil_scoped_release>(),
        py::doc("The name of the level\n"
                "External Read:SharedReadWrite lock required."));
    LevelMetadata.def_property_readonly(
        "modified_time",
        &Amulet::LevelMetadata::get_modified_time,
        py::call_guard<py::gil_scoped_release>(),
        py::doc("The time when the level was last modified.\n"
                "External Read:SharedReadWrite lock required."));
    LevelMetadata.def_property_readonly(
        "sub_chunk_size",
        &Amulet::LevelMetadata::get_sub_chunk_size,
        py::doc("The size of the sub-chunk. Must be a cube.\n"
                "External Read:SharedReadWrite lock required."));

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
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Open the level.\n"
                "\n"
                "If the level is already open, this does nothing.\n"
                "External ReadWrite:Unique lock required."));
    Amulet::def_signal(
        Level,
        "purged",
        &Amulet::Level::purged,
        py::doc("Signal emitted when the level is purged\n"
                "Thread safe."));
    Level.def(
        "purge",
        &Amulet::Level::purge,
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Clear all unsaved changes and restore points.\n"
                "External ReadWrite:Unique lock required."));
    Level.def(
        "save",
        &Amulet::Level::save,
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Save all changes to the level.\n"
                "External ReadWrite:Unique lock required."));
    Amulet::def_signal(
        Level,
        "closed",
        &Amulet::Level::closed,
        py::doc("Signal emitted when the level is closed.\n"
                "Thread safe."));
    Level.def(
        "close",
        &Amulet::Level::close,
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Close the level.\n"
                "External ReadWrite:Unique lock required.\n"
                "\n"
                "If the level is not open, this does nothing."));
    Amulet::def_signal(
        Level,
        "history_changed",
        &Amulet::Level::history_changed,
        py::doc("A signal emitted when the undo or redo count changes.\n"
                "Thread safe."));
    Level.def(
        "create_restore_point",
        &Amulet::Level::create_restore_point,
        py::call_guard<py::gil_scoped_release>(),
        py::doc(
            "Create a new history restore point.\n"
            "Any changes made after this point can be reverted by calling undo.\n"
            "External Read:SharedReadWrite lock required."));
    Level.def(
        "get_undo_count",
        &Amulet::Level::get_undo_count,
        py::call_guard<py::gil_scoped_release>(),
        py::doc(
            "Get the number of times undo can be called.\n"
            "External Read:SharedReadWrite lock required.\n"
            "External Read:SharedReadOnly lock optional."));
    Level.def(
        "undo",
        &Amulet::Level::undo,
        py::call_guard<py::gil_scoped_release>(),
        py::doc(
            "Revert the changes made since the previous restore point.\n"
            "External ReadWrite:SharedReadWrite lock required.\n"
            "External ReadWrite:Unique lock optional."));
    Level.def(
        "get_redo_count",
        &Amulet::Level::get_redo_count,
        py::call_guard<py::gil_scoped_release>(),
        py::doc(
            "Get the number of times redo can be called.\n"
            "External Read:SharedReadWrite lock required.\n"
            "External Read:SharedReadOnly lock optional."));
    Level.def(
        "redo",
        &Amulet::Level::redo,
        py::call_guard<py::gil_scoped_release>(),
        py::doc(
            "Redo changes that were previously reverted.\n"
            "External ReadWrite:SharedReadWrite lock required.\n"
            "External ReadWrite:Unique lock optional."));
    Amulet::def_signal(
        Level,
        "history_enabled_changed",
        &Amulet::Level::history_enabled_changed,
        py::doc("A signal emitted when set_history_enabled is called.\n"
                "Thread safe."));
    Level.def_property(
        "history_enabled",
        &Amulet::Level::get_history_enabled,
        &Amulet::Level::set_history_enabled,
        py::doc(
            "A boolean tracking if the history system is enabled.\n"
            "External Read:SharedReadWrite lock required when getting.\n"
            "External ReadWrite:SharedReadWrite lock required when setting.\n"
            "\n"
            "If true, the caller must call :meth:`create_restore_point` before making changes.\n"
            ":attr:`history_enabled_changed` is emitted when this is set."));
    Level.def(
        "dimension_ids",
        &Amulet::Level::get_dimension_ids,
        py::call_guard<py::gil_scoped_release>(),
        py::doc("The identifiers for all dimensions in the level.\n"
                "External Read:SharedReadWrite lock required.\n"
                "External Read:SharedReadOnly lock optional."));
    Level.def(
        "get_dimension",
        &Amulet::Level::get_dimension,
        py::arg("dimension_id"),
        py::doc("Get a dimension.\n"
                "External Read:SharedReadWrite lock required.\n"
                "External ReadWrite:SharedReadWrite lock required when calling code in Dimension (and its children) that need write permission."));

    py::class_<Amulet::CompactibleLevel, std::shared_ptr<Amulet::CompactibleLevel>> CompactibleLevel(m, "CompactibleLevel");
    CompactibleLevel.def(
        "compact",
        &Amulet::CompactibleLevel::compact,
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Compact the level data to reduce file size.\n"
                "External ReadWrite:SharedReadWrite lock required."));

    py::class_<Amulet::DiskLevel, std::shared_ptr<Amulet::DiskLevel>> DiskLevel(m, "DiskLevel");
    DiskLevel.def_property_readonly(
        "path",
        [](Amulet::DiskLevel& self) { return self.get_path().string(); },
        py::doc("The path to the level on disk.\n"
                "External Read:SharedReadWrite lock required."));

    py::class_<Amulet::ReloadableLevel, std::shared_ptr<Amulet::ReloadableLevel>> ReloadableLevel(m, "ReloadableLevel");
    ReloadableLevel.def(
        "reload_metadata",
        &Amulet::ReloadableLevel::reload_metadata,
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Reload the level metadata.\n"
                "This can only be done when the level is not open.\n"
                "External ReadWrite:Unique lock required."));
    Amulet::def_signal(
        ReloadableLevel,
        "reloaded",
        &Amulet::ReloadableLevel::reloaded,
        py::doc("Signal emitted when the level is reloaded.\n"
                "Thread safe."));
    ReloadableLevel.def(
        "reload",
        &Amulet::ReloadableLevel::reload,
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Reload the level.\n"
                "This is like closing and opening the level but does not release locks.\n"
                "This can only be done when the level is open."
                "External ReadWrite:Unique lock required."));

    return m;
}
