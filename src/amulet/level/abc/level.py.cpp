#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <memory>

#include <pybind11_extensions/py_module.hpp>

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
            ":param task_manager: The cancel manager through which cancel can be requested.\n"
            ":return: True if the level is open otherwise False.\n"
            ":raises amulet.utils.task_manager.TaskCancelled: If the task is cancelled."));
    LevelMetadata.def_property_readonly("platform", &Amulet::LevelMetadata::platform);
    LevelMetadata.def_property_readonly("max_game_version", &Amulet::LevelMetadata::max_game_version, py::return_value_policy::automatic);
    LevelMetadata.def_property_readonly(
        "level_name",
        &Amulet::LevelMetadata::level_name,
        py::doc("The human-readable name of the level"));
    LevelMetadata.def_property_readonly(
        "modified_time",
        &Amulet::LevelMetadata::modified_time,
        py::doc("The unix float timestamp of when the level was last modified."));
    LevelMetadata.def_property_readonly(
        "sub_chunk_size",
        &Amulet::LevelMetadata::sub_chunk_size,
        py::doc("The dimensions of a sub-chunk."));

    py::class_<
        Amulet::Level,
        std::shared_ptr<Amulet::Level>,
        Amulet::LevelMetadata>
        Level(m, "Level");
    Level.def(
        "open",
        &Amulet::Level::open,
        py::doc(
            "Open the level.\n"
            "\n"
            "If the level is already open, this does nothing.\n"
            "\n"
            ":param task_manager: The cancel manager through which cancel can be requested.\n"
            ":raises amulet.utils.task_manager.TaskCancelled: If the task is cancelled."));
    Level.def(
        "purge",
        &Amulet::Level::purge,
        py::doc(
            "Unload all loaded data.\n"
            "This is a nuclear function and must be used with :meth:`lock_unique`\n"
            "\n"
            "This is functionally the same as closing and reopening the level."));
    Level.def(
        "save",
        &Amulet::Level::save,
        py::doc(
            "Save all changes to the level"));
    Level.def(
        "close",
        &Amulet::Level::close,
        py::doc(
            "Close the level.\n"
            "\n"
            "If the level is not open, this does nothing.\n"
            "\n"
            ":param task_manager: The cancel manager through which cancel can be requested.\n"
            ":raises amulet.utils.task_manager.TaskCancelled: If the task is cancelled."));
    Level.def(
        "dimension_ids",
        &Amulet::Level::dimension_ids);
    Level.def(
        "get_dimension",
        &Amulet::Level::get_dimension,
        py::arg("dimension_id"));

    py::class_<Amulet::CompactibleLevel, std::shared_ptr<Amulet::CompactibleLevel>> CompactibleLevel(m, "CompactibleLevel");
    CompactibleLevel.def("compact", &Amulet::CompactibleLevel::compact);

    py::class_<Amulet::DiskLevel, std::shared_ptr<Amulet::DiskLevel>> DiskLevel(m, "DiskLevel");
    DiskLevel.def("path", [](Amulet::DiskLevel& self) { return self.path().string(); });

    py::class_<Amulet::ReloadableLevel, std::shared_ptr<Amulet::ReloadableLevel>> ReloadableLevel(m, "ReloadableLevel");
    ReloadableLevel.def("reload", &Amulet::ReloadableLevel::reload);

    return m;
}
