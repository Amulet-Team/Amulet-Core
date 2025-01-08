#include <memory>

#include <pybind11/pybind11.h>
#include <pybind11_extensions/py_module.hpp>

#include "dimension.hpp"

namespace py = pybind11;

py::module init_dimension(py::module m_parent)
{
    auto m = m_parent.def_submodule("dimension");

    py::class_<Amulet::Dimension, std::shared_ptr<Amulet::Dimension>> Dimension(m, "Dimension");
    Dimension.def_property_readonly("dimension_id", &Amulet::Dimension::dimension_id);
    Dimension.def("default_block", &Amulet::Dimension::default_block);
    Dimension.def("default_biome", &Amulet::Dimension::default_biome);
    Dimension.def("get_chunk_handle", &Amulet::Dimension::get_chunk_handle, py::arg("cx"), py::arg("cz"));

    return m;
}
