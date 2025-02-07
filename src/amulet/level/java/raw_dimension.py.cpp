#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

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
    JavaRawDimension.def_property_readonly(
        "lock",
        &Amulet::JavaRawDimension::get_mutex);
    JavaRawDimension.def_property_readonly(
        "dimension_id",
        &Amulet::JavaRawDimension::get_dimension_id);
    JavaRawDimension.def_property_readonly(
        "relative_path",
        &Amulet::JavaRawDimension::get_relative_path);
    JavaRawDimension.def_property_readonly(
        "bounds",
        &Amulet::JavaRawDimension::get_bounds);
    JavaRawDimension.def_property_readonly(
        "default_block",
        &Amulet::JavaRawDimension::get_default_block);
    JavaRawDimension.def_property_readonly(
        "default_biome",
        &Amulet::JavaRawDimension::get_default_biome);
    JavaRawDimension.def_property_readonly(
        "all_chunk_coords",
        [](const Amulet::JavaRawDimension& self) {
            return py::make_iterator(
                self.all_chunk_coords(),
                Amulet::AnvilChunkCoordIterator());
        });
    JavaRawDimension.def(
        "has_chunk",
        &Amulet::JavaRawDimension::has_chunk,
        py::arg("cx"),
        py::arg("cz"));
    JavaRawDimension.def(
        "delete_chunk",
        &Amulet::JavaRawDimension::delete_chunk,
        py::arg("cx"),
        py::arg("cz"));
    JavaRawDimension.def(
        "get_raw_chunk",
        &Amulet::JavaRawDimension::get_raw_chunk,
        py::arg("cx"),
        py::arg("cz"));
    JavaRawDimension.def(
        "set_raw_chunk",
        &Amulet::JavaRawDimension::set_raw_chunk,
        py::arg("cx"),
        py::arg("cz"),
        py::arg("chunk"));
    JavaRawDimension.def(
        "decode_chunk",
        [](
            Amulet::JavaRawDimension& self,
            const Amulet::JavaRawChunk& raw_chunk,
            std::int64_t cx,
            std::int64_t cz) -> std::shared_ptr<Amulet::JavaChunk> {
            return self.decode_chunk(raw_chunk, cx, cz);
        },
        py::arg("raw_chunk"),
        py::arg("cx"),
        py::arg("cz"));
    JavaRawDimension.def(
        "encode_chunk",
        &Amulet::JavaRawDimension::encode_chunk,
        py::arg("chunk"),
        py::arg("cx"),
        py::arg("cz"));
    JavaRawDimension.def(
        "compact",
        &Amulet::JavaRawDimension::compact);

    return m;
}
