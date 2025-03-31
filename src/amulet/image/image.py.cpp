#include <pybind11/pybind11.h>

#include <filesystem>

#include <pybind11_extensions/py_module.hpp>

#include "image.hpp"


namespace py = pybind11;

void init_image(py::module m_parent)
{
    auto m = pybind11_extensions::def_subpackage(m_parent, "image");
    py::list __path__ = m.attr("__path__");
    std::filesystem::path path = __path__[0].cast<std::string>();
    
    m.def("get_missing_no_icon", &Amulet::get_missing_no_icon);
    m.def("get_missing_pack_icon", &Amulet::get_missing_pack_icon);
    m.def("get_missing_world_icon", &Amulet::get_missing_world_icon);

    m.attr("missing_no_icon_path") = py::cast((path / "missing_no.png").string());
    m.attr("missing_pack_icon_path") = py::cast((path / "missing_pack.png").string());
    m.attr("missing_world_icon_path") = py::cast((path / "missing_world.png").string());

}
