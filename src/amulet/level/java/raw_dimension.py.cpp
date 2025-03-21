#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <memory>

#include <amulet/utils/holder.py.hpp>

#include "raw_dimension.hpp"

namespace py = pybind11;

py::module init_java_raw_dimension(py::module m_parent)
{
    auto m = m_parent.def_submodule("raw_dimension");

    py::class_<
        Amulet::JavaRawDimension,
        Amulet::nogil_shared_ptr<Amulet::JavaRawDimension>>
        JavaRawDimension(m, "JavaRawDimension");
    JavaRawDimension.def_property_readonly(
        "lock",
        &Amulet::JavaRawDimension::get_mutex,
        py::keep_alive<0, 1>(),
        py::doc("The public lock\n"
                "Thread safe."));
    JavaRawDimension.def_property_readonly(
        "dimension_id",
        &Amulet::JavaRawDimension::get_dimension_id,
        py::doc("The identifier for this dimension. eg. \"minecraft:overworld\".\n"
                "Thread safe."));
    JavaRawDimension.def_property_readonly(
        "relative_path",
        &Amulet::JavaRawDimension::get_relative_path,
        py::doc("The relative path to the dimension. eg. \"DIM1\".\n"
                "Thread safe."));
    JavaRawDimension.def_property_readonly(
        "bounds",
        &Amulet::JavaRawDimension::get_bounds,
        py::doc("The selection box that fills the whole world.\n"
                "Thread safe."));
    JavaRawDimension.def_property_readonly(
        "default_block",
        &Amulet::JavaRawDimension::get_default_block,
        py::doc("The default block for this dimension.\n"
                "Thread safe."));
    JavaRawDimension.def_property_readonly(
        "default_biome",
        &Amulet::JavaRawDimension::get_default_biome,
        py::doc("The default biome for this dimension.\n"
                "Thread safe."));
    JavaRawDimension.def_property_readonly(
        "all_chunk_coords",
        [](const Amulet::JavaRawDimension& self) {
            return py::make_iterator(
                self.all_chunk_coords(),
                Amulet::AnvilChunkCoordIterator());
        },
        py::doc("An iterator of all chunk coordinates in the dimension.\n"
                "External Read:SharedReadWrite lock required.\n"
                "External Read:SharedReadOnly lock optional."));
    JavaRawDimension.def(
        "has_chunk",
        &Amulet::JavaRawDimension::has_chunk,
        py::arg("cx"),
        py::arg("cz"),
        py::doc("Does the chunk exist in this dimension.\n"
                "External Read:SharedReadWrite lock required.\n"
                "External Read:SharedReadOnly lock optional."));
    JavaRawDimension.def(
        "delete_chunk",
        &Amulet::JavaRawDimension::delete_chunk,
        py::arg("cx"),
        py::arg("cz"),
        py::doc("Delete the chunk from this dimension.\n"
                "External ReadWrite:SharedReadWrite lock required."));
    JavaRawDimension.def(
        "get_raw_chunk",
        &Amulet::JavaRawDimension::get_raw_chunk,
        py::arg("cx"),
        py::arg("cz"),
        py::doc("Get the raw chunk from this dimension.\n"
                "External Read:SharedReadWrite lock required."));
    JavaRawDimension.def(
        "set_raw_chunk",
        &Amulet::JavaRawDimension::set_raw_chunk,
        py::arg("cx"),
        py::arg("cz"),
        py::arg("chunk"),
        py::doc("Set the chunk in this dimension from raw data.\n"
                "External ReadWrite:SharedReadWrite lock required."));
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
        py::arg("cz"),
        py::doc("Decode a raw chunk to a chunk object.\n"
                "TODO: thread safety"));
    JavaRawDimension.def(
        "encode_chunk",
        &Amulet::JavaRawDimension::encode_chunk,
        py::arg("chunk"),
        py::arg("cx"),
        py::arg("cz"),
        py::doc("Encode a chunk object to its raw data.\n"
                "TODO: thread safety"));
    JavaRawDimension.def(
        "compact",
        &Amulet::JavaRawDimension::compact,
        py::doc("Compact the level.\n"
                "External Read:SharedReadWrite lock required."));
    JavaRawDimension.def(
        "destroy",
        &Amulet::JavaRawDimension::destroy,
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Destroy the instance.\n"
                "Calls made after this will fail.\n"
                "This may only be called by the owner of the instance.\n"
                "External ReadWrite:Unique lock required."));
    JavaRawDimension.def(
        "is_destroyed",
        &Amulet::JavaRawDimension::is_destroyed,
        py::doc("Has the instance been destroyed.\n"
                "If this is false, other calls will fail.\n"
                "External Read:SharedReadWrite lock required."));

    return m;
}
