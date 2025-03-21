#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <amulet/utils/holder.py.hpp>

#include "region.hpp"

namespace py = pybind11;

py::module init_anvil_region(py::module m_parent)
{
    py::module m = m_parent.def_submodule("region");

    py::class_<Amulet::AnvilRegion, Amulet::nogil_shared_ptr<Amulet::AnvilRegion>> AnvilRegion(m, "AnvilRegion",
        "A class to read and write Minecraft Java Edition Region files.\n"
        "Only one instance should exist per region file at any given time otherwise bad things may happen.\n"
        "This class is internally thread safe but a public lock is provided to enable external synchronisation.\n"
        "Upstream locks from the level must also be adhered to.");

    py::class_<Amulet::AnvilRegion::FileCloser, std::shared_ptr<Amulet::AnvilRegion::FileCloser>>
        FileCloser(AnvilRegion, "FileCloser",
            "A class to manage closing the region file.\n"
            "When the instance is deleted the region file will be closed.\n"
            "The region file can be manually closed before this is deleted.");

    AnvilRegion.def(
        py::init(
            [](std::string directory, std::string file_name, std::int64_t rx, std::int64_t rz, bool mcc) {
                return std::make_shared<Amulet::AnvilRegion>(directory, file_name, rx, rz, mcc);
            }),
        py::arg("directory"),
        py::arg("file_name"),
        py::arg("rx"),
        py::arg("rz"),
        py::arg("mcc") = false,
        py::doc("Construct from the directory path, name of the file and region coordinates."));
    AnvilRegion.def(
        py::init(
            [](std::string directory, std::int64_t rx, std::int64_t rz, bool mcc) {
                return std::make_shared<Amulet::AnvilRegion>(directory, rx, rz, mcc);
            }),
        py::arg("directory"),
        py::arg("rx"),
        py::arg("rz"),
        py::arg("mcc") = false,
        py::doc("Construct from the directory path and region coordinates.\n"
                "File name is computed from region coordinates."));
    AnvilRegion.def(
        py::init(
            [](std::string path, bool mcc) {
                return std::make_shared<Amulet::AnvilRegion>(path, mcc);
            }),
        py::arg("path"),
        py::arg("mcc") = false,
        py::doc("Construct from the path to the region file.\n"
                "Coordinates are computed from the file name.\n"
                "File name must match \"r.X.Z.mca\"."));

    AnvilRegion.def_property_readonly(
        "lock",
        &Amulet::AnvilRegion::get_mutex,
        py::keep_alive<0, 1>(),
        py::doc("A lock which can be used to synchronise calls.\n"
                "Thread safe."));
    AnvilRegion.def_property_readonly(
        "path",
        [](Amulet::AnvilRegion& self) -> std::string { return self.path().string(); },
        py::doc("The path of the region file.\n"
                "Thread safe."));
    AnvilRegion.def_property_readonly(
        "rx",
        &Amulet::AnvilRegion::rx,
        py::doc("The region x coordinate of the file.\n"
                "Thread safe."));
    AnvilRegion.def_property_readonly(
        "rz",
        &Amulet::AnvilRegion::rz,
        py::doc("The region z coordinate of the file.\n"
                "Thread safe."));

    AnvilRegion.def(
        "get_coords",
        &Amulet::AnvilRegion::get_coords,
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Get the coordinates of all values in the region file.\n"
                "Coordinates are in world space.\n"
                "External Read:SharedReadWrite lock required.\n"
                "External Read:SharedReadOnly lock optional."));
    AnvilRegion.def(
        "contains",
        &Amulet::AnvilRegion::contains,
        py::arg("cx"),
        py::arg("cz"),
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Is the coordinate in the region.\n"
                "This returns true even if there is no value for the coordinate.\n"
                "Coordinates are in world space.\n"
                "Thread safe."));
    AnvilRegion.def(
        "has_value",
        &Amulet::AnvilRegion::has_value,
        py::arg("cx"),
        py::arg("cz"),
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Is there a value stored for this coordinate.\n"
                "Coordinates are in world space.\n"
                "External Read:SharedReadWrite lock required.\n"
                "External Read:SharedReadOnly lock optional."));
    AnvilRegion.def(
        "get_value",
        &Amulet::AnvilRegion::get_value,
        py::arg("cx"),
        py::arg("cz"),
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Get the value for this coordinate.\n"
                "Coordinates are in world space.\n"
                "External Read:SharedReadWrite lock required."));
    AnvilRegion.def(
        "set_value",
        &Amulet::AnvilRegion::set_value,
        py::arg("cx"),
        py::arg("cz"),
        py::arg("tag"),
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Set the value for this coordinate.\n"
                "Coordinates are in world space.\n"
                "External ReadWrite:SharedReadWrite lock required."));
    AnvilRegion.def(
        "delete_value",
        &Amulet::AnvilRegion::delete_value,
        py::arg("cx"),
        py::arg("cz"),
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Delete the chunk data.\n"
                "Coordinates are in world space.\n"
                "External ReadWrite:SharedReadWrite lock required."));
    AnvilRegion.def(
        "delete_batch",
        &Amulet::AnvilRegion::delete_batch,
        py::arg("coords"),
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Delete multiple chunk's data.\n"
                "Coordinates are in world space.\n"
                "External ReadWrite:SharedReadWrite lock required."));
    AnvilRegion.def(
        "compact",
        &Amulet::AnvilRegion::compact,
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Compact the region file.\n"
                "Defragments the file and deletes unused space.\n"
                "If there are no chunks remaining in the region file it will be deleted.\n"
                "External ReadWrite:SharedReadWrite lock required."));
    AnvilRegion.def(
        "close",
        &Amulet::AnvilRegion::close,
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Close the file object if open.\n"
                "This is automatically called when the instance is destroyed but may be called earlier.\n"
                "Thread safe."));
    AnvilRegion.def(
        "destroy",
        &Amulet::AnvilRegion::destroy,
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Destroy the instance.\n"
                "Calls made after this will fail.\n"
                "This may only be called by the owner of the instance.\n"
                "External ReadWrite:Unique lock required."));
    AnvilRegion.def(
        "is_destroyed",
        &Amulet::AnvilRegion::is_destroyed,
        py::doc("Has the instance been destroyed.\n"
                "If this is false, other calls will fail.\n"
                "External Read:SharedReadWrite lock required."));
    AnvilRegion.def(
        "get_file_closer",
        &Amulet::AnvilRegion::get_file_closer,
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Get the object responsible for closing the region file.\n"
                "When this object is deleted it will close the region file\n"
                "This means that holding a reference to this will delay when the region file is closed.\n"
                "The region file may still be closed manually before this object is deleted.\n"
                "Thread safe."));

    py::register_exception<Amulet::RegionDoesNotExist>(m, "RegionDoesNotExist", PyExc_RuntimeError);

    return m;
}
