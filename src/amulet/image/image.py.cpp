#include <pybind11/pybind11.h>

#include <pybind11_extensions/py_module.hpp>

#include "image.hpp"


namespace py = pybind11;

void init_image(py::module m_parent)
{
    auto m = pybind11_extensions::def_subpackage(m_parent, "image");
    
    m.def("get_missing_no_icon", &Amulet::get_missing_no_icon);
    m.def("get_missing_pack_icon", &Amulet::get_missing_pack_icon);
    m.def("get_missing_world_icon", &Amulet::get_missing_world_icon);

}
