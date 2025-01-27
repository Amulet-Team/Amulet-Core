#include <pybind11/pybind11.h>

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
        &Amulet::Dimension::dimension_id,
        py::doc("The dimension identifier this chunk is from."));
    Dimension.def(
        "default_block", 
        &Amulet::Dimension::default_block,
        py::doc("The default block for this dimension")
    );
    Dimension.def(
        "default_biome", 
        &Amulet::Dimension::default_biome,
        py::doc("The default biome for this dimension")
    );
    Dimension.def(
        "get_chunk_handle", 
        &Amulet::Dimension::get_chunk_handle, 
        py::arg("cx"), 
        py::arg("cz"),
        py::doc(
            "Get the chunk handle for the given chunk in this dimension.\n"
            "\n"
            ":param cx: The chunk x coordinate to load.\n"
            ":param cz: The chunk z coordinate to load."
        )
    );

    return m;
}
