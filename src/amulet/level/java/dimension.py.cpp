#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <memory>

#include "dimension.hpp"

namespace py = pybind11;

py::module init_java_dimension(py::module m_parent)
{
    auto m = m_parent.def_submodule("dimension");

    m.attr("JavaInternalDimensionID") = py::module::import("builtins").attr("str");

    py::class_<
        Amulet::JavaDimension,
        Amulet::Dimension,
        std::shared_ptr<Amulet::JavaDimension>>
        JavaDimension(m, "JavaDimension");

    return m;
}
