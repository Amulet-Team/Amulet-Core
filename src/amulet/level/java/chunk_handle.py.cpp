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
    JavaChunkHandle.attr("get_chunk") = py::cpp_function(
        [](Amulet::JavaChunkHandle& self) -> std::shared_ptr<Amulet::JavaChunk> {
            return self.get_java_chunk();
        },
        py::name("get_chunk"),
        py::is_method(JavaChunkHandle),
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Get a unique copy of the chunk data."));
    JavaChunkHandle.attr("set_chunk") = py::cpp_function(
        &Amulet::JavaChunkHandle::set_java_chunk,
        py::name("set_chunk"),
        py::is_method(JavaChunkHandle),
        py::arg("chunk"),
        py::call_guard<py::gil_scoped_release>(),
        py::doc("Overwrite the chunk data."));

    return m;
}
