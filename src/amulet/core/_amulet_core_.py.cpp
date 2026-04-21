#include <pybind11/pybind11.h>

namespace py = pybind11;

void init_version(py::module);
void init_selection(py::module);
void init_block(py::module);
void init_block_entity(py::module);
void init_entity(py::module);
void init_biome(py::module);
void init_palette(py::module);
void init_chunk(py::module);

void init_amulet_core(py::module m)
{
    init_version(m);
    init_selection(m);
    init_block(m);
    init_block_entity(m);
    init_entity(m);
    init_biome(m);
    init_palette(m);
    init_chunk(m);
}
