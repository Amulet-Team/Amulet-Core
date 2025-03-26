#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <memory>

#include <pybind11_extensions/py_module.hpp>

#include "dimension.hpp"

namespace py = pybind11;

py::module init_dimension(py::module m_parent)
{
    auto m = m_parent.def_submodule("dimension");

    py::class_<Amulet::Dimension, std::shared_ptr<Amulet::Dimension>> Dimension(m, "Dimension");
    Dimension.def_property_readonly(
        "dimension_id",
        &Amulet::Dimension::get_dimension_id,
        py::doc("Get the dimension id for this dimension.\n"
                "Thread safe."));
    Dimension.def_property_readonly(
        "bounds",
        &Amulet::Dimension::get_bounds,
        py::doc("The editable region of the dimension.\n"
                "Thread safe."));
    Dimension.def_property_readonly(
        "default_block",
        &Amulet::Dimension::get_default_block,
        py::keep_alive<0, 1>(),
        py::doc("The default block for this dimension.\n"
                "Thread safe."));
    Dimension.def_property_readonly(
        "default_biome",
        &Amulet::Dimension::get_default_biome,
        py::keep_alive<0, 1>(),
        py::doc("The default biome for this dimension\n"
                "Thread safe."));
    Dimension.def(
        "get_chunk_handle",
        &Amulet::Dimension::get_chunk_handle,
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
