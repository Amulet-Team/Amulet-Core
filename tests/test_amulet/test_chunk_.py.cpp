#include <pybind11/pybind11.h>

#include <amulet/chunk/chunk.hpp>

namespace py = pybind11;

void init_test_chunk(py::module m_parent){
    auto m = m_parent.def_submodule("test_chunk_");
    m.def("throw_chunk_does_not_exist", [](){ throw Amulet::ChunkDoesNotExist(); });
    m.def("throw_chunk_load_error", [](){ throw Amulet::ChunkLoadError(); });
}
