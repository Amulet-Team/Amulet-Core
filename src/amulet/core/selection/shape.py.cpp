#include <pybind11/pybind11.h>
#include <pybind11/typing.h>

#include "shape.hpp"

namespace py = pybind11;

py::object init_selection_shape(py::module m_parent)
{
    auto m = m_parent.def_submodule("shape");
    py::classh<Amulet::SelectionShape> SelectionShape(m, "SelectionShape",
        "A base class for selection classes.");

    SelectionShape.def(
        "voxelise",
        &Amulet::SelectionShape::voxelise,
        py::doc("Convert the shape into unit voxels."));

    return SelectionShape;
}
