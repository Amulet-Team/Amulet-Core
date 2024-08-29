#include <memory>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/operators.h>
#include <pybind11/typing.h>
#include <amulet/pybind11/collections.hpp>

#include <amulet_nbt/tag/named_tag.hpp>

#include <amulet/collections/holder.py.hpp>
#include <amulet/collections/mutable_mapping.py.hpp>
#include <amulet/level/java/chunk_components/java_raw_chunk_component.hpp>

namespace py = pybind11;


void init_java_raw_chunk_component(py::module m) {
    py::module::import("amulet_nbt");

    py::class_<Amulet::JavaRawChunkComponent, std::shared_ptr<Amulet::JavaRawChunkComponent>>
    JavaRawChunkComponent(m, "JavaRawChunkComponent");

    JavaRawChunkComponent.def_property_readonly_static(
        "ComponentID",
        [](py::object) {
            return Amulet::JavaRawChunkComponent::ComponentID;
        }
    );
    JavaRawChunkComponent.def_property(
        "raw_data",
        [](
            Amulet::JavaRawChunkComponent& self
        ) -> py::collections::MutableMapping<std::string, AmuletNBT::NamedTag> {
            auto raw_data = self.get_raw_data();
            return py::cast(
                std::make_shared<Amulet::collections::Map<Amulet::JavaRawChunkType>>(
                    *raw_data,
                    py::cast(Amulet::collections::HolderTemplate(raw_data))
                )
            );
        },
        [](
            Amulet::JavaRawChunkComponent& self, py::collections::Mapping<std::string, AmuletNBT::NamedTag> py_raw_data
        ){
            auto raw_data = std::make_shared<Amulet::JavaRawChunkType>();
            for (auto it = py_raw_data.begin(); it != py_raw_data.end(); it++){
                raw_data->insert_or_assign(
                    it->cast<std::string>(),
                    py_raw_data.attr("__getitem__")(*it).cast<AmuletNBT::NamedTag>()
                );
            }
            self.set_raw_data(raw_data);
        }
    );
}
