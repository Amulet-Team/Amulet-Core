#include <pybind11/operators.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/typing.h>

#include <amulet/pybind11_extensions/py_module.hpp>

#include "chunk.hpp"

namespace py = pybind11;
namespace pyext = Amulet::pybind11_extensions;

void init_chunk_components(py::module);

void init_chunk(py::module m_parent)
{
    auto m = pyext::def_subpackage(m_parent, "chunk");
    init_chunk_components(m);

    py::class_<Amulet::Chunk, std::shared_ptr<Amulet::Chunk>> Chunk(m, "Chunk",
        "A base class for all chunk classes.");
    Chunk.def_property_readonly(
        "chunk_id",
        &Amulet::Chunk::get_chunk_id);
    Chunk.def_property_readonly(
        "component_ids",
        &Amulet::Chunk::get_component_ids);
    auto py_serialise = [](const Amulet::Chunk& self) -> py::typing::Dict<py::str, py::typing::Optional<py::bytes>> {
        Amulet::SerialisedChunkComponents chunk_data;
        {
            ;
            py::gil_scoped_release gil;
            chunk_data = self.serialise_chunk();
        }
        py::dict data;
        for (const auto& [k, v] : chunk_data) {
            if (v) {
                data[py::str(k)] = py::bytes(v.value());
            } else {
                data[py::str(k)] = py::none();
            }
        }
        return data;
    };
    Chunk.def(
        "serialise_chunk",
        py_serialise,
        py::doc("This is private. Do not use this. It will be removed in the future."));
    auto py_deserialise = [](Amulet::Chunk& self, py::typing::Dict<py::str, py::typing::Optional<py::bytes>> data) {
        Amulet::SerialisedChunkComponents component_data;
        for (const auto& [k, v] : data) {
            if (v.is(py::none())) {
                component_data[k.cast<std::string>()];
            } else {
                component_data[k.cast<std::string>()] = v.cast<std::string>();
            }
        }
        {
            py::gil_scoped_release gil;
            self.reconstruct_chunk(component_data);
        }
    };
    Chunk.def(
        "reconstruct_chunk",
        py_deserialise,
        py::doc("This is private. Do not use this. It will be removed in the future."));
    Chunk.def(
        py::pickle(
            [py_serialise](const Amulet::Chunk& self) {
                return py::make_tuple(
                    self.get_chunk_id(),
                    py_serialise(self));
            },
            [py_deserialise](py::tuple state) {
                if (state.size() != 2) {
                    throw std::runtime_error("Invalid state!");
                }
                auto self = Amulet::get_null_chunk(state[0].cast<std::string>());
                py_deserialise(*self, state[1]);
                return self;
            }));

    m.def(
        "get_null_chunk",
        &Amulet::get_null_chunk,
        py::doc("This is a private function"));

    auto ChunkLoadError = py::register_exception<Amulet::ChunkLoadError>(m, "ChunkLoadError", PyExc_RuntimeError);
    ChunkLoadError.doc() = "An error thrown if a chunk failed to load for some reason.\n"
                           "\n"
                           "This may be due to a corrupt chunk, an unsupported chunk format or just because the chunk does not exist to be loaded.\n"
                           "\n"
                           "Catching this error will also catch :class:`ChunkDoesNotExist`\n"
                           "\n"
                           ">>> try:\n"
                           ">>>     # get chunk\n"
                           ">>>     chunk = world.get_chunk(cx, cz, dimension)\n"
                           ">>> except ChunkLoadError:\n"
                           ">>>     # will catch all chunks that have failed to load\n"
                           ">>>     # either because they do not exist or errored during loading.";
    auto ChunkDoesNotExist = py::register_exception<Amulet::ChunkDoesNotExist>(m, "ChunkDoesNotExist", ChunkLoadError);
    ChunkDoesNotExist.doc() = "An error thrown if a chunk does not exist and therefor cannot be loaded.\n"
                              "\n"
                              ">>> try:\n"
                              ">>>     # get chunk\n"
                              ">>>     chunk = world.get_chunk(cx, cz, dimension)\n"
                              ">>> except ChunkDoesNotExist:\n"
                              ">>>     # will catch all chunks that do not exist\n"
                              ">>>     # will not catch corrupt chunks\n"
                              ">>> except ChunkLoadError:\n"
                              ">>>     # will only catch chunks that errored during loading\n"
                              ">>>     # chunks that do not exist were caught by the previous except section.";
}
