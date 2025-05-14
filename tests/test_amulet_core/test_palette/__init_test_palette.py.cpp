#include <pybind11/pybind11.h>

#include <amulet/pybind11_extensions/py_module.hpp>

namespace py = pybind11;
namespace pyext = Amulet::pybind11_extensions;

void init_test_biome_palette(py::module);
void init_test_block_palette(py::module);

void init_test_palette(py::module m_parent)
{
    auto m = pyext::def_subpackage(m_parent, "test_palette");
    init_test_biome_palette(m);
    init_test_block_palette(m);
}
