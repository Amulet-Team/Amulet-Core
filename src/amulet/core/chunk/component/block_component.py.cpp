#include <pybind11/operators.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <limits>
#include <memory>
#include <variant>

#include <amulet/core/version/version.hpp>

#include "block_component.hpp"

namespace py = pybind11;

py::module init_block_component(py::module m_parent)
{
    auto m = m_parent.def_submodule("block_component");

    py::class_<Amulet::BlockComponentData, std::shared_ptr<Amulet::BlockComponentData>>
        BlockComponentData(m, "BlockComponentData");
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
        &Amulet::BlockComponentData::get_palette_ptr);
    BlockComponentData.def_property_readonly(
        "sections",
        &Amulet::BlockComponentData::get_sections_ptr);

    py::class_<Amulet::BlockComponent, std::shared_ptr<Amulet::BlockComponent>>
        BlockComponent(m, "BlockComponent");
    BlockComponent.def_readonly_static(
        "ComponentID",
        &Amulet::BlockComponent::ComponentID);
    BlockComponent.def_property(
        "block",
        &Amulet::BlockComponent::get_block,
        &Amulet::BlockComponent::set_block);

    return m;
}
