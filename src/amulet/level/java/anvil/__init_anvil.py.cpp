#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <pybind11_extensions/py_module.hpp>

#include "region.hpp"

namespace py = pybind11;

py::module init_anvil_region(py::module);
py::module init_anvil_dimension(py::module);

void init_java_anvil(py::module m_parent)
{
    auto m = pybind11_extensions::def_subpackage(m_parent, "anvil");

    auto region = init_anvil_region(m);
    auto dimension = init_anvil_dimension(m);

    m.attr("AnvilRegion") = region.attr("AnvilRegion");
    m.attr("RegionDoesNotExist") = region.attr("RegionDoesNotExist");
    m.attr("AnvilDimensionLayer") = dimension.attr("AnvilDimensionLayer");
    m.attr("AnvilDimension") = dimension.attr("AnvilDimension");
    m.attr("RawChunkType") = dimension.attr("RawChunkType");
}
