#include <pybind11/pybind11.h>

#include <amulet/level/java/anvil/region.hpp>

namespace py = pybind11;

void init_test_region(py::module m_parent){
    auto m = m_parent.def_submodule("test_region_");
    m.def("throw_region_does_not_exist", [](){ throw Amulet::RegionDoesNotExist(); });
}
