#include <pybind11/pybind11.h>

#include <memory>

#include <amulet/version.hpp>

#include "raw_level.hpp"

namespace py = pybind11;

py::module init_java_raw_level(py::module m_parent)
{
    auto m = m_parent.def_submodule("raw_level");

    py::class_<
        Amulet::JavaRawLevel,
        std::shared_ptr<Amulet::JavaRawLevel>>
        JavaRawLevel(m, "JavaRawLevel");

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

    return m;
}
