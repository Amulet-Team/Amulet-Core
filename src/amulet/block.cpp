#include "abc.hpp"
//include amuletcpp/version.cpp
#include <amuletcpp/block.hpp>
//include amuletcpp/block.cpp


namespace py = pybind11;

PYBIND11_MODULE(block, m) {
    py::object PlatformVersionContainer = py::module_::import("amulet.version").attr("PlatformVersionContainer");

    py::class_<Amulet::Block, std::shared_ptr<Amulet::Block>> Block(m, "Block", PlatformVersionContainer);
        Block.def(
            py::init<const Amulet::PlatformType&, const Amulet::VersionNumber&, const std::string&, const std::string&>(),
            py::arg("platform"), py::arg("version"), py::arg("namespace"), py::arg("base_name"));
        Block.def_readonly("namespace", &Amulet::Block::namespace_);
        Block.def_readonly("base_name", &Amulet::Block::base_name);
}
