#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <memory>

#include "chunk_handle.hpp"

namespace py = pybind11;

py::module init_java_chunk_handle(py::module m_parent)
{
    auto m = m_parent.def_submodule("chunk_handle");

    py::class_<
        Amulet::JavaChunkHandle,
        Amulet::ChunkHandle,
        std::shared_ptr<Amulet::JavaChunkHandle>>
        JavaChunkHandle(m, "JavaChunkHandle");

    return m;
}
