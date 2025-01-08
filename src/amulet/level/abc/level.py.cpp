#include <memory>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11_extensions/py_module.hpp>

#include "level.hpp"

namespace py = pybind11;

py::module init_level_abc_level(py::module m_parent)
{
    auto m = pybind11_extensions::def_subpackage(m_parent, "level");

    py::class_<Amulet::LevelMetadata, std::shared_ptr<Amulet::LevelMetadata>> LevelMetadata(m, "LevelMetadata");
    LevelMetadata.def("is_open", &Amulet::LevelMetadata::is_open);
    LevelMetadata.def_property_readonly("platform", &Amulet::LevelMetadata::platform);
    LevelMetadata.def_property_readonly("max_game_version", &Amulet::LevelMetadata::max_game_version);
    LevelMetadata.def_property_readonly("level_name", &Amulet::LevelMetadata::level_name);
    LevelMetadata.def_property_readonly("modified_time", &Amulet::LevelMetadata::modified_time);
    LevelMetadata.def_property_readonly("sub_chunk_size", &Amulet::LevelMetadata::sub_chunk_size);

    py::class_<
        Amulet::Level,
        std::shared_ptr<Amulet::Level>,
        Amulet::LevelMetadata>
        Level(m, "Level");
    Level.def("open", &Amulet::Level::open);
    Level.def("purge", &Amulet::Level::purge);
    Level.def("save", &Amulet::Level::save);
    Level.def("close", &Amulet::Level::close);
    Level.def("dimension_ids", &Amulet::Level::dimension_ids);
    Level.def("get_dimension", &Amulet::Level::get_dimension, py::arg("dimension_id"));

    return m;
}
