#include <pybind11/pybind11.h>

#include <amulet/pybind11_extensions/py_module.hpp>

namespace py = pybind11;
namespace pyext = Amulet::pybind11_extensions;

py::module init_section_array_map(py::module);
py::module init_block_component(py::module);

void init_chunk_components(py::module m_parent)
{
    auto m = pyext::def_subpackage(m_parent, "component");

    auto m_section_array_map = init_section_array_map(m);
    m.attr("IndexArray3D") = m_section_array_map.attr("IndexArray3D");
    m.attr("SectionArrayMap") = m_section_array_map.attr("SectionArrayMap");

    auto m_block_component = init_block_component(m);
    m.attr("BlockComponentData") = m_block_component.attr("BlockComponentData");
    m.attr("BlockComponent") = m_block_component.attr("BlockComponent");
}
