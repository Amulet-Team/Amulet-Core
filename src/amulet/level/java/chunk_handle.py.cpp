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
    JavaChunkHandle.def(
        "set_chunk",
        &Amulet::JavaChunkHandle::set_java_chunk,
        py::arg("chunk"),
        py::prepend(),
        py::call_guard<py::gil_scoped_release>(),
        py::doc(
            "Overwrite the chunk data.\n"
            "You must acquire the chunk lock before setting.\n"
            "If you want to edit the chunk, use :meth:`edit` instead.\n"
            "\n"
            ":param chunk: The chunk data to set."));
    // This is here to appease mypy.
    JavaChunkHandle.def(
        "set_chunk",
        &Amulet::JavaChunkHandle::set_chunk,
        py::arg("chunk"),
        py::call_guard<py::gil_scoped_release>(),
        py::doc(
            "Overwrite the chunk data.\n"
            "You must acquire the chunk lock before setting.\n"
            "If you want to edit the chunk, use :meth:`edit` instead.\n"
            "\n"
            ":param chunk: The chunk data to set."));

    return m;
}
