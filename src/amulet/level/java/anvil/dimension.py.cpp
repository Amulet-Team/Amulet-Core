#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <pybind11_extensions/collections.hpp>

#include "dimension.hpp"
namespace py = pybind11;

void init_anvil_dimension(py::module m)
{
    py::class_<Amulet::AnvilDimensionLayer, std::shared_ptr<Amulet::AnvilDimensionLayer>> AnvilDimensionLayer(m, "AnvilDimensionLayer");
    AnvilDimensionLayer.def(
        py::init(
            [](std::string directory, bool mcc) {
                return std::make_shared<Amulet::AnvilDimensionLayer>(directory, mcc);
            }),
        py::arg("directory"),
        py::arg("mcc") = false);
    // AnvilDimensionLayer.def("all_region_coords", &Amulet::AnvilDimensionLayer::all_region_coords);
    AnvilDimensionLayer.def(
        "has_region",
        &Amulet::AnvilDimensionLayer::has_region,
        py::arg("rx"),
        py::arg("rz"));
    AnvilDimensionLayer.def(
        "get_region",
        &Amulet::AnvilDimensionLayer::get_region,
        py::arg("rx"),
        py::arg("rz"),
        py::arg("create") = false);
    AnvilDimensionLayer.def(
        "has_chunk",
        &Amulet::AnvilDimensionLayer::has_chunk,
        py::arg("cx"),
        py::arg("cz"));
    AnvilDimensionLayer.def(
        "get_chunk_data",
        &Amulet::AnvilDimensionLayer::get_chunk_data,
        py::arg("cx"),
        py::arg("cz"));
    AnvilDimensionLayer.def(
        "set_chunk_data",
        &Amulet::AnvilDimensionLayer::set_chunk_data,
        py::arg("cx"),
        py::arg("cz"),
        py::arg("tag"));
    AnvilDimensionLayer.def(
        "delete_chunk",
        &Amulet::AnvilDimensionLayer::delete_chunk,
        py::arg("cx"),
        py::arg("cz"));
    AnvilDimensionLayer.def(
        "compact",
        &Amulet::AnvilDimensionLayer::compact);

    py::class_<Amulet::AnvilDimension, std::shared_ptr<Amulet::AnvilDimension>> AnvilDimension(m, "AnvilDimension");
    AnvilDimension.def(
        py::init(
            [](std::string directory, pybind11_extensions::Iterable<std::string> layer_names, bool mcc) {
                return std::make_shared<Amulet::AnvilDimension>(directory, layer_names, mcc);
            }),
        py::arg("directory"),
        py::arg("layer_names"),
        py::arg("mcc") = false);
    AnvilDimension.def(
        "has_layer",
        &Amulet::AnvilDimension::has_layer,
        py::arg("layer_name"));
    AnvilDimension.def(
        "get_layer",
        &Amulet::AnvilDimension::get_layer,
        py::arg("layer_name"));
    AnvilDimension.def(
        "all_chunk_coords",
        &Amulet::AnvilDimension::all_chunk_coords);
    AnvilDimension.def(
        "has_chunk",
        &Amulet::AnvilDimension::has_chunk,
        py::arg("cx"),
        py::arg("cz"));
    AnvilDimension.def(
        "get_chunk_data",
        &Amulet::AnvilDimension::get_chunk_data,
        py::arg("cx"),
        py::arg("cz"));
    AnvilDimension.def(
        "set_chunk_data",
        &Amulet::AnvilDimension::set_chunk_data,
        py::arg("cx"),
        py::arg("cz"),
        py::arg("data_layers")
        );
    AnvilDimension.def(
        "delete_chunk",
        &Amulet::AnvilDimension::delete_chunk,
        py::arg("cx"),
        py::arg("cz"));
    AnvilDimension.def(
        "compact",
        &Amulet::AnvilDimension::compact);
}
