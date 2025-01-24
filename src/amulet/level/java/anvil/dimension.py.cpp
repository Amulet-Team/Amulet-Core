#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <pybind11_extensions/collections.hpp>

#include "dimension.hpp"

namespace py = pybind11;

py::module init_anvil_dimension(py::module m_parent)
{
    py::module m = m_parent.def_submodule("dimension");

    py::class_<Amulet::AnvilDimensionLayer, std::shared_ptr<Amulet::AnvilDimensionLayer>> AnvilDimensionLayer(m, "AnvilDimensionLayer",
        "A class to manage a directory of region files.");
    AnvilDimensionLayer.def(
        py::init(
            [](std::string directory, bool mcc) {
                return std::make_shared<Amulet::AnvilDimensionLayer>(directory, mcc);
            }),
        py::arg("directory"),
        py::arg("mcc") = false);
    AnvilDimensionLayer.def_property_readonly(
        "directory",
        [](const Amulet::AnvilDimensionLayer& self) {
            return self.directory().string();
        },
        py::doc("The directory this instance manages."));
    AnvilDimensionLayer.def_property_readonly(
        "mcc",
        &Amulet::AnvilDimensionLayer::mcc,
        py::doc("Is mcc file support enabled for this instance."));
    AnvilDimensionLayer.def(
        "all_region_coords",
        [](Amulet::AnvilDimensionLayer& self) {
            return py::make_iterator(
                self.all_region_coords(),
                Amulet::AnvilRegionCoordIterator());
        },
        py::doc("An iterator of all region coordinates in this layer."));
    AnvilDimensionLayer.def(
        "has_region",
        &Amulet::AnvilDimensionLayer::has_region,
        py::arg("rx"),
        py::arg("rz"),
        py::doc("Check if a region file exists in this layer."));
    AnvilDimensionLayer.def(
        "get_region",
        &Amulet::AnvilDimensionLayer::get_region,
        py::arg("rx"),
        py::arg("rz"),
        py::arg("create") = false,
        py::doc("Get an AnvilRegion instance. This must not be stored long-term."));
    AnvilDimensionLayer.def(
        "all_chunk_coords",
        [](std::shared_ptr<Amulet::AnvilDimensionLayer> self) {
            return py::make_iterator(
                Amulet::AnvilChunkCoordIterator(std::move(self)),
                Amulet::AnvilChunkCoordIterator());
        },
        py::doc("An iterator of all chunk coordinates in this layer."));
    AnvilDimensionLayer.def(
        "has_chunk",
        &Amulet::AnvilDimensionLayer::has_chunk,
        py::arg("cx"),
        py::arg("cz"),
        py::doc("Check if the chunk has data in this layer."));
    AnvilDimensionLayer.def(
        "get_chunk_data",
        &Amulet::AnvilDimensionLayer::get_chunk_data,
        py::arg("cx"),
        py::arg("cz"),
        py::doc(
            "Get a NamedTag of a chunk from the database.\n"
            "Will raise ChunkDoesNotExist if the region or chunk does not exist"));
    AnvilDimensionLayer.def(
        "set_chunk_data",
        &Amulet::AnvilDimensionLayer::set_chunk_data,
        py::arg("cx"),
        py::arg("cz"),
        py::arg("tag"),
        py::doc("Set the chunk data for this layer."));
    AnvilDimensionLayer.def(
        "delete_chunk",
        &Amulet::AnvilDimensionLayer::delete_chunk,
        py::arg("cx"),
        py::arg("cz"),
        py::doc("Delete the chunk data from this layer."));
    AnvilDimensionLayer.def(
        "compact",
        &Amulet::AnvilDimensionLayer::compact,
        py::doc("Defragment the region files and remove unused region files."));

    py::class_<Amulet::AnvilDimension, std::shared_ptr<Amulet::AnvilDimension>> AnvilDimension(m, "AnvilDimension",
        "A class to manage the data for a dimension.\n"
        "This can consist of multiple layers. Eg the region layer which contains chunk data and the entities layer which contains entities.");
    AnvilDimension.def(
        py::init(
            [](std::string directory, pybind11_extensions::Iterable<std::string> layer_names, bool mcc) {
                return std::make_shared<Amulet::AnvilDimension>(directory, layer_names, mcc);
            }),
        py::arg("directory"),
        py::arg("layer_names"),
        py::arg("mcc") = false);
    AnvilDimension.def_property_readonly(
        "directory",
        [](const Amulet::AnvilDimension& self) {
            return self.directory().string();
        },
        py::doc("The directory this dimension is in."));
    AnvilDimension.def_property_readonly(
        "mcc",
        &Amulet::AnvilDimension::mcc,
        py::doc("Are mcc files enabled for this dimension."));
    AnvilDimension.def_property_readonly(
        "layer_names",
        &Amulet::AnvilDimension::layer_names,
        py::doc("Get the names of all layers in this dimension."));
    AnvilDimension.def(
        "has_layer",
        &Amulet::AnvilDimension::has_layer,
        py::arg("layer_name"),
        py::doc("Check if this dimension has the requested layer."));
    AnvilDimension.def(
        "get_layer",
        &Amulet::AnvilDimension::get_layer,
        py::arg("layer_name"),
        py::doc("Get the AnvilDimensionLayer for a specific layer. The returned value must not be stored long-term."));
    AnvilDimension.def(
        "all_chunk_coords",
        [](Amulet::AnvilDimension& self) {
            return py::make_iterator(
                self.all_chunk_coords(),
                Amulet::AnvilChunkCoordIterator());
        },
        py::doc("Get an iterator for all the chunks that exist in this dimension."));
    AnvilDimension.def(
        "has_chunk",
        &Amulet::AnvilDimension::has_chunk,
        py::arg("cx"),
        py::arg("cz"),
        py::doc("Check if a chunk exists."));
    AnvilDimension.def(
        "get_chunk_data",
        &Amulet::AnvilDimension::get_chunk_data,
        py::arg("cx"),
        py::arg("cz"),
        py::doc("Get the data for a chunk"));
    AnvilDimension.def(
        "set_chunk_data",
        &Amulet::AnvilDimension::set_chunk_data<pybind11_extensions::Iterable<std::pair<std::string, AmuletNBT::NamedTag>>>,
        py::arg("cx"),
        py::arg("cz"),
        py::arg("data_layers"),
        py::doc("Set the data for a chunk."));
    AnvilDimension.def(
        "delete_chunk",
        &Amulet::AnvilDimension::delete_chunk,
        py::arg("cx"),
        py::arg("cz"),
        py::doc("Delete all data for the given chunk."));
    AnvilDimension.def(
        "compact",
        &Amulet::AnvilDimension::compact,
        py::doc("Defragment the region files and remove unused region files."));

    auto dict = py::module::import("builtins").attr("dict");
    auto str = py::module::import("builtins").attr("str");
    auto NamedTag = py::module::import("amulet_nbt").attr("NamedTag");
    m.attr("RawChunkType") = dict.attr("__class_getitem__")(py::make_tuple(str, NamedTag));

    return m;
}
