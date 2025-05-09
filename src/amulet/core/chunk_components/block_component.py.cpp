#include <pybind11/operators.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <limits>
#include <memory>
#include <variant>

#include <amulet/core/version/version.hpp>

#include "block_component.hpp"

namespace py = pybind11;

void init_block_component(py::module block_component_module)
{
    py::class_<Amulet::BlockComponentData, std::shared_ptr<Amulet::BlockComponentData>>
        BlockComponentData(block_component_module, "BlockComponentData");

    BlockComponentData.def(
        py::init<
            const Amulet::VersionRange&,
            const Amulet::SectionShape&,
            const Amulet::BlockStack&>(),
        py::arg("version_range"),
        py::arg("array_shape"),
        py::arg("default_block"));
    BlockComponentData.def_property_readonly(
        "palette",
        &Amulet::BlockComponentData::get_palette);
    BlockComponentData.def_property_readonly(
        "sections",
        &Amulet::BlockComponentData::get_sections);

    py::class_<Amulet::BlockComponent, std::shared_ptr<Amulet::BlockComponent>>
        BlockComponent(block_component_module, "BlockComponent");
    BlockComponent.def_readonly_static(
        "ComponentID",
        &Amulet::BlockComponent::ComponentID);
    BlockComponent.def_property(
        "block",
        &Amulet::BlockComponent::get_block,
        &Amulet::BlockComponent::set_block);
}
