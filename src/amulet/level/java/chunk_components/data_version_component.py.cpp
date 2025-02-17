#include <pybind11/operators.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <amulet/level/java/chunk_components/data_version_component.hpp>

namespace py = pybind11;

void init_data_version_component(py::module data_version_component_module)
{
    py::class_<Amulet::DataVersionComponent, std::shared_ptr<Amulet::DataVersionComponent>>
        DataVersionComponent(data_version_component_module, "DataVersionComponent");

    DataVersionComponent.def_readonly_static(
        "ComponentID",
        &Amulet::DataVersionComponent::ComponentID);
    DataVersionComponent.def_property_readonly(
        "data_version",
        &Amulet::DataVersionComponent::get_data_version);
}
