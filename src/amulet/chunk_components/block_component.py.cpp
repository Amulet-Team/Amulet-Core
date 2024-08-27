#include <memory>
#include <variant>
#include <limits>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/operators.h>

#include <amulet/version.hpp>
#include <amulet/chunk_components/block_component.hpp>


namespace py = pybind11;

void init_block_component(py::module block_component_module) {
    py::module::import("amulet.palette.block_palette");
    py::module::import("amulet.chunk_components.section_array_map");

    py::class_<Amulet::BlockComponentData, std::shared_ptr<Amulet::BlockComponentData>>
        BlockComponentData(block_component_module, "BlockComponentData");
    
    BlockComponentData.def(
        py::init<
            std::shared_ptr<Amulet::VersionRange>,
            const Amulet::SectionShape&,
            std::shared_ptr<Amulet::BlockStack>
        >(),
        py::arg("version_range"),
        py::arg("array_shape"),
        py::arg("default_block")
    );
    BlockComponentData.def_property_readonly(
        "palette",
        &Amulet::BlockComponentData::get_palette
    );
    BlockComponentData.def_property_readonly(
        "sections",
        &Amulet::BlockComponentData::get_sections
    );

    py::class_<Amulet::BlockComponent, std::shared_ptr<Amulet::BlockComponent>>
        BlockComponent(block_component_module, "BlockComponent");
    BlockComponent.def_property_readonly_static(
        "ComponentID",
        [](py::object) {
            return Amulet::BlockComponent::ComponentID;
        }
    );
    BlockComponent.def_property(
        "block",
        &Amulet::BlockComponent::get_block,
        &Amulet::BlockComponent::set_block
    );
}
