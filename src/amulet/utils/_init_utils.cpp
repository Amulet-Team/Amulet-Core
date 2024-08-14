#include <pybind11/pybind11.h>
namespace py = pybind11;

void init_utils_collections(py::module);
void init_utils_numpy(py::module);

void init_utils(py::module utils_module){
    auto utils_numpy_module = utils_module.def_submodule("numpy");
    init_utils_numpy(utils_numpy_module);

    auto utils_collections_module = utils_module.def_submodule("collections");
    init_utils_collections(utils_collections_module);

    utils_module.def(
        "__getattr__",
        [utils_module](py::object name) -> py::object {
            if (
                name == py::str("block_coords_to_chunk_coords") ||
                name == py::str("chunk_coords_to_region_coords") ||
                name == py::str("region_coords_to_chunk_coords") ||
                name == py::str("blocks_slice_to_chunk_slice") ||
                name == py::str("from_nibble_array")
            ){
                py::object attr = py::module::import("amulet.utils.world_utils").attr(name);
                utils_module.attr(name) = attr;
                return attr;
            } else if (
                name == py::str("check_all_exist") ||
                name == py::str("check_one_exists") ||
                name == py::str("load_leveldat")
            ){
                py::object attr = py::module::import("amulet.utils.format_utils").attr(name);
                utils_module.attr(name) = attr;
                return attr;
            } else {
                throw py::attribute_error("module amulet.utils has no attribute " + py::repr(name).cast<std::string>());
            }
        }
    );

    py::list all;
    all.append("block_coords_to_chunk_coords");
    all.append("chunk_coords_to_region_coords");
    all.append("region_coords_to_chunk_coords");
    all.append("blocks_slice_to_chunk_slice");
    all.append("from_nibble_array");
    all.append("check_all_exist");
    all.append("check_one_exists");
    all.append("load_leveldat");
    utils_module.attr("__all__") = all;
}
