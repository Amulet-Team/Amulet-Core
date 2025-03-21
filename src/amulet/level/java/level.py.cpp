#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <memory>

#include "level.hpp"
#include <amulet/level/abc/level.hpp>

namespace py = pybind11;

py::module init_java_level(py::module m_parent)
{
    auto m = m_parent.def_submodule("level");

    py::class_<
        Amulet::JavaLevel,
        Amulet::Level,
        Amulet::CompactibleLevel,
        Amulet::DiskLevel,
        Amulet::ReloadableLevel,
        std::shared_ptr<Amulet::JavaLevel>>
        JavaLevel(m, "JavaLevel");
    JavaLevel.def_static(
        "load",
        [](std::string path) -> std::shared_ptr<Amulet::JavaLevel> {
            return Amulet::JavaLevel::load(path);
        },
        py::arg("path"),
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Load an existing Java level from the given directory.\n"
                "Thread safe."));
    JavaLevel.def_static(
        "create",
        [](const Amulet::JavaCreateArgsV1& args) -> std::shared_ptr<Amulet::JavaLevel> {
            return Amulet::JavaLevel::create(args);
        },
        py::arg("args"),
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Create a new Java level at the given directory.\n"
                "Thread safe."));
    JavaLevel.def_property_readonly(
        "raw_level",
        &Amulet::JavaLevel::get_raw_level,
        py::keep_alive<0, 1>(),
        py::doc(
            "Access the raw level instance.\n"
            "Before calling any mutating functions, the caller must call :meth:`purge` (optionally saving before)\n"
            "External ReadWrite:Unique lock required."));

    return m;
}
