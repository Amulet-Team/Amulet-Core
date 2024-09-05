#include <amulet/chunk.hpp>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/operators.h>
#include <pybind11/typing.h>


namespace py = pybind11;

void init_chunk(py::module m_parent) {
    auto m = m_parent.def_submodule("chunk");
    py::class_<Amulet::Chunk, std::shared_ptr<Amulet::Chunk>> Chunk(m, "Chunk",
        "A base class for all chunk classes."
    );
        Chunk.def_property_readonly(
            "chunk_id",
            &Amulet::Chunk::get_chunk_id
        );
        Chunk.def_property_readonly(
            "component_ids",
            &Amulet::Chunk::get_component_ids
        );
        auto py_serialise = [](const Amulet::Chunk& self) -> py::typing::Dict<py::str, py::typing::Optional<py::bytes>> {
            py::dict data;
            for (const auto& [k, v] : self.serialise_chunk()) {
                if (v) {
                    data[py::str(k)] = py::bytes(v.value());
                }
                else {
                    data[py::str(k)] = py::none();
                }
            }
            return data;
        };
        Chunk.def(
            "serialise_chunk",
            py_serialise,
            py::doc("This is private. Do not use this. It will be removed in the future.")
        );
        auto py_deserialise = [](Amulet::Chunk& self, py::typing::Dict<py::str, py::typing::Optional<py::bytes>> data) {
            Amulet::SerialisedComponents component_data;
            for (const auto& [k, v] : data) {
                if (v.is(py::none())) {
                    component_data[k.cast<std::string>()];
                }
                else {
                    component_data[k.cast<std::string>()] = v.cast<std::string>();
                }
            }
            self.reconstruct_chunk(component_data);
        };
        Chunk.def(
            "reconstruct_chunk",
            py_deserialise,
            py::doc("This is private. Do not use this. It will be removed in the future.")
        );
        Chunk.def(
            py::pickle(
                [py_serialise](const Amulet::Chunk& self) {
                    return py::make_tuple(
                        self.get_chunk_id(),
                        py_serialise(self)
                    );
                },
                [py_deserialise](py::tuple state) {
                    if (state.size() != 2) { throw std::runtime_error("Invalid state!"); }
                    auto self = Amulet::get_null_chunk(state[0].cast<std::string>());
                    py_deserialise(*self, state[1]);
                    return self;
                }
            )
        );

    m.def(
        "get_null_chunk", 
        &Amulet::get_null_chunk,
        py::doc("This is a private function")
    );
}
