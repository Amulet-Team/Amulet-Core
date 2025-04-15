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
    JavaDimension.attr("get_chunk_handle") = py::cpp_function(
        &Amulet::JavaDimension::get_java_chunk_handle,
        py::name("get_chunk_handle"),
        py::is_method(JavaDimension),
        py::arg("cx"),
        py::arg("cz"),
        py::call_guard<py::gil_scoped_release>(),
        py::doc(
            "Get the chunk handle for the given chunk in this dimension.\n"
            "Thread safe.\n"
            "\n"
            ":param cx: The chunk x coordinate to load.\n"
            ":param cz: The chunk z coordinate to load."));

    return m;
}
