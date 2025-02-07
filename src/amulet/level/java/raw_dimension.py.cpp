#include <pybind11/pybind11.h>

#include <memory>

#include "raw_dimension.hpp"

namespace py = pybind11;

py::module init_java_raw_dimension(py::module m_parent)
{
    auto m = m_parent.def_submodule("raw_dimension");

    py::class_<
        Amulet::JavaRawDimension,
        std::shared_ptr<Amulet::JavaRawDimension>>
        JavaRawDimension(m, "JavaRawDimension");

    return m;
}
