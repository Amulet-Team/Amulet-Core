#include <memory>

#include <pybind11/pybind11.h>
#include <pybind11_extensions/py_module.hpp>

#include "chunk_handle.hpp"

namespace py = pybind11;

py::module init_chunk_handle(py::module m_parent)
{
    auto m = pybind11_extensions::def_subpackage(m_parent, "chunk_handle");

    py::class_<Amulet::ChunkHandle, std::shared_ptr<Amulet::ChunkHandle>> ChunkHandle(m, "ChunkHandle");
    ChunkHandle.def_property_readonly("dimension_id", &Amulet::ChunkHandle::dimension_id);
    ChunkHandle.def_property_readonly("cx", &Amulet::ChunkHandle::cx);
    ChunkHandle.def_property_readonly("cz", &Amulet::ChunkHandle::cz);
    ChunkHandle.def("exists", &Amulet::ChunkHandle::exists);
    ChunkHandle.def("get_chunk", &Amulet::ChunkHandle::get_chunk);
    ChunkHandle.def("set_chunk", &Amulet::ChunkHandle::set_chunk, py::arg("chunk"));
    ChunkHandle.def("delete_chunk", &Amulet::ChunkHandle::delete_chunk);

    return m;
}
