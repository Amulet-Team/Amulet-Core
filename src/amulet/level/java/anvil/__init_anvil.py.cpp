#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <pybind11_extensions/py_module.hpp>

#include "region.hpp"
namespace py = pybind11;

void init_anvil_region(py::module);

void init_java_anvil(py::module m_parent)
{
    auto m = pybind11_extensions::def_subpackage(m_parent, "anvil");

    init_anvil_region(m);
    init_anvil_dimension(m);

    m.attr("AnvilDimension") = py::module::import("amulet.level.java.anvil._dimension").attr("AnvilDimension");
    m.attr("AnvilDimensionLayer") = py::module::import("amulet.level.java.anvil._dimension").attr("AnvilDimensionLayer");
    m.attr("RawChunkType") = py::module::import("amulet.level.java.anvil._dimension").attr("RawChunkType");
}
