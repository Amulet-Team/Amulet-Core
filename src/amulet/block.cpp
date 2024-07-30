#include <amulet/block.hpp>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/operators.h>


namespace py = pybind11;

PYBIND11_MODULE(block, m) {
    py::object PlatformVersionContainer = py::module_::import("amulet.version").attr("PlatformVersionContainer");

    py::class_<Amulet::Block, std::shared_ptr<Amulet::Block>> Block(m, "Block", PlatformVersionContainer);
        Block.def(
            py::init<
                const Amulet::PlatformType&,
                const Amulet::VersionNumber&,
                const std::string&,
                const std::string&,
                const std::map<std::string, Amulet::PropertyValueType>&
            >(),
            py::arg("platform"),
            py::arg("version"),
            py::arg("namespace"),
            py::arg("base_name"),
            py::arg("properties") = py::tuple()
        );
        Block.def_property_readonly(
            "namespace",
            &Amulet::Block::get_namespace
        );
        Block.def_property_readonly(
            "base_name",
            &Amulet::Block::get_base_name
        );
        Block.def_property_readonly(
            "properties",
            &Amulet::Block::get_properties
        );
        Block.def(
            "__repr__",
            [](const Amulet::Block& self){
                return "Block(" +
                    py::repr(py::cast(self.get_platform())).cast<std::string>() + ", " +
                    py::repr(py::cast(self.get_version())).cast<std::string>() + ", " +
                    py::repr(py::cast(self.get_namespace())).cast<std::string>() + ", " +
                    py::repr(py::cast(self.get_base_name())).cast<std::string>() +
                ")";
            }
        );
        Block.def(
            py::pickle(
                [](const Amulet::Block& self) -> py::bytes {
                    return py::bytes(Amulet::serialise(self));
                },
                [](py::bytes state){
                    return Amulet::deserialise<Amulet::Block>(state.cast<std::string>());
                }
            )
        );
}
