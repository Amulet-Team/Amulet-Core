#include <pybind11/pybind11.h>

#include <memory>

#include <pybind11_extensions/py_module.hpp>

#include <amulet/utils/signal.py.hpp>

#include "chunk_handle.hpp"

namespace py = pybind11;

py::module init_chunk_handle(py::module m_parent)
{
    auto m = m_parent.def_submodule("chunk_handle");

    py::class_<Amulet::ChunkHandle, std::shared_ptr<Amulet::ChunkHandle>> ChunkHandle(m, "ChunkHandle");
    Amulet::def_signal(
        ChunkHandle,
        "changed",
        &Amulet::ChunkHandle::changed,
        py::doc("Signal emitted when the chunk data changes."));
    ChunkHandle.def_property_readonly(
        "lock",
        &Amulet::ChunkHandle::get_mutex,
        py::keep_alive<0, 1>(),
        py::doc("The public lock.\n"
                "Thread safe."));
    ChunkHandle.def_property_readonly(
        "dimension_id",
        &Amulet::ChunkHandle::get_dimension_id,
        py::doc("The dimension identifier this chunk is from."));
    ChunkHandle.def_property_readonly(
        "cx",
        &Amulet::ChunkHandle::get_cx,
        py::doc("The chunk x coordinate."));
    ChunkHandle.def_property_readonly(
        "cz",
        &Amulet::ChunkHandle::get_cz,
        py::doc("The chunk z coordinate."));
    ChunkHandle.def(
        "exists",
        &Amulet::ChunkHandle::exists,
        py::call_guard<py::gil_scoped_release>(),
        py::doc(
            "Does the chunk exist. This is a quick way to check if the chunk exists without loading it.\n"
            "\n"
            "This state may change if the lock is not acquired.\n"
            "\n"
            ":return: True if the chunk exists. Calling get on this chunk handle may still throw ChunkLoadError"));
    ChunkHandle.def(
        "get_chunk",
        [](Amulet::ChunkHandle& self) -> std::shared_ptr<Amulet::Chunk> {
            return self.get_chunk();
        },
        py::call_guard<py::gil_scoped_release>(),
        py::doc(
            "Get a unique copy of the chunk data.\n"
            "\n"
            "If you want to edit the chunk, use :meth:`edit` instead.\n"
            "\n"
            "If you only want to access/modify parts of the chunk data you can specify the components you want to load.\n"
            "This makes it faster because you don't need to load unneeded parts.\n"
            "\n"
            ":param components: None to load all components or an iterable of component strings to load.\n"
            ":return: A unique copy of the chunk data."));
    ChunkHandle.def(
        "set_chunk",
        &Amulet::ChunkHandle::set_chunk,
        py::arg("chunk"),
        py::call_guard<py::gil_scoped_release>(),
        py::doc(
            "Overwrite the chunk data.\n"
            "You must acquire the chunk lock before setting.\n"
            "If you want to edit the chunk, use :meth:`edit` instead.\n"
            "\n"
            ":param chunk: The chunk data to set."));
    ChunkHandle.def(
        "delete_chunk",
        &Amulet::ChunkHandle::delete_chunk,
        py::call_guard<py::gil_scoped_release>(),
        py::doc(
            "Delete the chunk from the level.\n"
            "You must acquire the chunk lock before deleting."));

    return m;
}
