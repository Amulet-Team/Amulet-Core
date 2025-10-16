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

    py::class_<Amulet::BlockStorage, std::shared_ptr<Amulet::BlockStorage>>
        BlockStorage(m, "BlockStorage");
    BlockStorage.def(
        py::init<
            const Amulet::VersionRange&,
            const Amulet::SectionShape&,
            const Amulet::BlockStack&>(),
        py::arg("version_range"),
        py::arg("array_shape"),
        py::arg("default_block"));
    BlockStorage.def_property_readonly(
        "palette",
        &Amulet::BlockStorage::get_palette_ptr);
    BlockStorage.def_property_readonly(
        "sections",
        &Amulet::BlockStorage::get_sections_ptr);

    py::class_<Amulet::BlockComponent, std::shared_ptr<Amulet::BlockComponent>>
        BlockComponent(m, "BlockComponent");
    BlockComponent.def_readonly_static(
        "ComponentID",
        &Amulet::BlockComponent::ComponentID);
    BlockComponent.def_property(
        "block_storage",
        &Amulet::BlockComponent::get_block_storage,
        &Amulet::BlockComponent::set_block_storage);

    return m;
}
