#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <pybind11_extensions/py_module.hpp>

#include "_region.hpp"
namespace py = pybind11;

void init_java_anvil(py::module m_parent)
{
    auto m = pybind11_extensions::def_subpackage(m_parent, "anvil");

    py::class_<Amulet::AnvilRegion, std::shared_ptr<Amulet::AnvilRegion>> AnvilRegion(m, "AnvilRegion");
    AnvilRegion.def(
        py::init(
            [](std::string directory, std::string file_name, std::int64_t rx, std::int64_t rz, bool mcc) {
                return std::make_shared<Amulet::AnvilRegion>(directory, file_name, rx, rz, mcc);
            }),
        py::arg("directory"),
        py::arg("file_name"),
        py::arg("rx"),
        py::arg("rz"),
        py::arg("mcc") = false);
    AnvilRegion.def(
        py::init(
            [](std::string directory, std::int64_t rx, std::int64_t rz, bool mcc) {
                return std::make_shared<Amulet::AnvilRegion>(directory, rx, rz, mcc);
            }),
        py::arg("directory"),
        py::arg("rx"),
        py::arg("rz"),
        py::arg("mcc") = false);
    AnvilRegion.def(
        py::init(
            [](std::string directory, bool mcc) {
                return std::make_shared<Amulet::AnvilRegion>(directory, mcc);
            }),
        py::arg("path"),
        py::arg("mcc") = false);

    AnvilRegion.def_property_readonly("path", [](Amulet::AnvilRegion& self) -> std::string { return self.path().string(); });
    AnvilRegion.def_property_readonly("rx", &Amulet::AnvilRegion::rx);
    AnvilRegion.def_property_readonly("rz", &Amulet::AnvilRegion::rz);
    
    AnvilRegion.def("all_coords", &Amulet::AnvilRegion::all_coords);
    AnvilRegion.def("has_data", &Amulet::AnvilRegion::has_data, py::arg("cx"), py::arg("cz"));
    AnvilRegion.def("get_data", &Amulet::AnvilRegion::get_data, py::arg("cx"), py::arg("cz"));
    AnvilRegion.def("set_data", &Amulet::AnvilRegion::set_data, py::arg("cx"), py::arg("cz"), py::arg("tag"));
    AnvilRegion.def("delete_data", &Amulet::AnvilRegion::delete_data, py::arg("cx"), py::arg("cz"));
    AnvilRegion.def("compact", &Amulet::AnvilRegion::compact);

    m.attr("AnvilDimension") = py::module::import("amulet.level.java.anvil._dimension").attr("AnvilDimension");
    m.attr("AnvilDimensionLayer") = py::module::import("amulet.level.java.anvil._dimension").attr("AnvilDimensionLayer");
    m.attr("RawChunkType") = py::module::import("amulet.level.java.anvil._dimension").attr("RawChunkType");
}
