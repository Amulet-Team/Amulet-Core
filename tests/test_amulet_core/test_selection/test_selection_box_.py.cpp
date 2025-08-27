#include <pybind11/pybind11.h>
#include <pybind11/typing.h>

#include <amulet/test_utils/test_utils.hpp>

#include <amulet/core/selection/box.hpp>

namespace py = pybind11;

void init_test_selection_box(py::module m_parent)
{
    auto m = m_parent.def_submodule("test_selection_box_");

    m.def(
        "get_tests",
        []() -> py::typing::List<py::typing::Callable<void()>> {
            py::list tests;

            return tests;
        });
}
