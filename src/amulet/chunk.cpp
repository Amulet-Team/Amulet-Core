#include <amulet/chunk.hpp>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/operators.h>


namespace py = pybind11;

void init_chunk(py::module m) {
    py::class_<Amulet::Chunk, std::shared_ptr<Amulet::Chunk>> Chunk(m, "Chunk",
        "A base class for all chunk classes."
    );
        Chunk.def(
            "chunk_id",
            &Amulet::Chunk::chunk_id
        );
}
