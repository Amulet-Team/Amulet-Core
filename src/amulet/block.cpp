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
                const std::string&
            >(),
            py::arg("platform"),
            py::arg("version"),
            py::arg("namespace"),
            py::arg("base_name")
        );
        Block.def_readonly(
            "namespace",
            &Amulet::Block::namespace_
        );
        Block.def_readonly(
            "base_name",
            &Amulet::Block::base_name
        );
        Block.def(
            "__repr__",
            [](const Amulet::Block& self){
                return "Block(" +
                    py::repr(py::cast(self.platform)).cast<std::string>() + ", " +
                    py::repr(py::cast(self.version)).cast<std::string>() + ", " +
                    py::repr(py::cast(self.namespace_)).cast<std::string>() + ", " +
                    py::repr(py::cast(self.base_name)).cast<std::string>() +
                ")";
            }
        );
//        Block.def(
//            py::pickle(
//                [](const Amulet::Block& self) -> py::bytes {
//                    PyErr_SetString(PyExc_NotImplementedError, "");
//                    throw py::error_already_set();
//                },
//                [](py::bytes state){
//                    PyErr_SetString(PyExc_NotImplementedError, "");
//                    throw py::error_already_set();
//                }
//            )
//        );
}
