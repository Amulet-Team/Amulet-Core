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

    py::classh<Amulet::BlockStorage>
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
        py::cpp_function(
            [](Amulet::BlockStorage& self) {
                return self.get_palette_ptr();
            },
            py::returns_non_null()));
    BlockStorage.def_property_readonly(
        "sections",
        py::cpp_function(
            [](Amulet::BlockStorage& self) {
                return self.get_sections_ptr();
            },
            py::returns_non_null()));

    py::classh<Amulet::BlockComponent>
        BlockComponent(m, "BlockComponent");
    BlockComponent.def_readonly_static(
        "ComponentID",
        &Amulet::BlockComponent::ComponentID);
    BlockComponent.def_property(
        "block_storage",
        py::cpp_function(
            [](Amulet::BlockComponent& self) {
                return self.get_block_storage_ptr();
            },
            py::returns_non_null(),
            py::is_method(BlockComponent)),
        py::cpp_function(
            &Amulet::BlockComponent::set_block_storage,
            py::is_method(BlockComponent),
            py::arg("block_storage").none(false)));

    return m;
}
