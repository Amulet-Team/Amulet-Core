#include <pybind11/pybind11.h>

#include <pybind11_extensions/py_module.hpp>

#include "block.hpp"

namespace py = pybind11;

void init_game_java(py::module);

void init_game_java_block(py::module m_parent)
{
    auto m = m_parent.def_submodule("block");
    std::string module_name = m.attr("__name__").cast<std::string>();

    py::enum_<Amulet::Waterloggable> Waterloggable(m, "Waterloggable");
    Waterloggable.value(
        "No",
        Amulet::Waterloggable::No,
        "Cannot be waterlogged.");
    Waterloggable.value(
        "Yes",
        Amulet::Waterloggable::Yes,
        "Can be waterlogged.");
    Waterloggable.value(
        "Always",
        Amulet::Waterloggable::Always,
        "Is always waterlogged. (attribute is not stored)");
    Waterloggable.attr("__repr__") = py::cpp_function(
        [module_name, Waterloggable](const py::object& arg) -> py::str {
            return py::str("{}.{}").format(module_name, Waterloggable.attr("__str__")(arg));
        },
        py::name("__repr__"),
        py::is_method(Waterloggable));
}
