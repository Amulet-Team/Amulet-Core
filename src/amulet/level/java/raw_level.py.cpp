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
        py::call_guard<py::gil_scoped_release>());
    JavaRawLevel.def_static(
        "create",
        [](const Amulet::JavaCreateArgsV1& args) -> std::shared_ptr<Amulet::JavaRawLevel> {
            return Amulet::JavaRawLevel::create(args);
        },
        py::arg("args"),
        py::call_guard<py::gil_scoped_release>());
    JavaRawLevel.def(
        "lock",
        &Amulet::JavaRawLevel::get_mutex);
    JavaRawLevel.def(
        "is_open",
        &Amulet::JavaRawLevel::is_open,
        py::call_guard<py::gil_scoped_release>());
    JavaRawLevel.def(
        "reload_metadata",
        &Amulet::JavaRawLevel::reload_metadata,
        py::call_guard<py::gil_scoped_release>());
    JavaRawLevel.def(
        "open",
        &Amulet::JavaRawLevel::open,
        py::call_guard<py::gil_scoped_release>());
    JavaRawLevel.def(
        "close",
        &Amulet::JavaRawLevel::close,
        py::call_guard<py::gil_scoped_release>());
    JavaRawLevel.def_property_readonly(
        "path",
        [](const Amulet::JavaRawLevel& self) {
            return self.get_path().string();
        });
    JavaRawLevel.def_property(
        "level_dat",
        &Amulet::JavaRawLevel::get_level_dat,
        &Amulet::JavaRawLevel::set_level_dat,
        py::call_guard<py::gil_scoped_release>());
    JavaRawLevel.def_property_readonly(
        "platform",
        &Amulet::JavaRawLevel::get_platform);
    JavaRawLevel.def_property(
        "data_version",
        &Amulet::JavaRawLevel::get_data_version,
        &Amulet::JavaRawLevel::set_data_version,
        py::call_guard<py::gil_scoped_release>());
    JavaRawLevel.def_property_readonly(
        "modified_time",
        &Amulet::JavaRawLevel::get_modified_time,
        py::call_guard<py::gil_scoped_release>());
    JavaRawLevel.def_property(
        "level_name",
        &Amulet::JavaRawLevel::get_level_name,
        &Amulet::JavaRawLevel::set_level_name);
    JavaRawLevel.def_property_readonly(
        "dimension_ids",
        &Amulet::JavaRawLevel::get_dimension_ids,
        py::call_guard<py::gil_scoped_release>());
    JavaRawLevel.def(
        "get_dimension",
        &Amulet::JavaRawLevel::get_dimension,
        py::arg("dimension_id"),
        py::call_guard<py::gil_scoped_release>());
    JavaRawLevel.def(
        "compact",
        &Amulet::JavaRawLevel::compact,
        py::call_guard<py::gil_scoped_release>());
    JavaRawLevel.def(
        "get_block_id_override",
        &Amulet::JavaRawLevel::get_block_id_override,
        py::call_guard<py::gil_scoped_release>());
    JavaRawLevel.def(
        "get_biome_id_override",
        &Amulet::JavaRawLevel::get_biome_id_override,
        py::call_guard<py::gil_scoped_release>());

    return m;
}
