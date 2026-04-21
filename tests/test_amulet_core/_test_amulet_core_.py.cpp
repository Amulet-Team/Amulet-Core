#include <pybind11/pybind11.h>

namespace py = pybind11;

void init_test_biome(py::module);
void init_test_block(py::module);
void init_test_block_entity(py::module);
void init_test_chunk(py::module);
void init_test_chunk_components(py::module);
void init_test_entity(py::module);
void init_test_palette(py::module);
void init_test_selection(py::module);
void init_test_version(py::module);

void init_test_amulet_core(py::module m){
    init_test_biome(m);
    init_test_block(m);
    init_test_block_entity(m);
    init_test_chunk(m);
    init_test_chunk_components(m);
    init_test_entity(m);
    init_test_palette(m);
    init_test_selection(m);
    init_test_version(m);
}
