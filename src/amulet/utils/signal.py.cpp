#include <pybind11/pybind11.h>

#include <amulet/utils/signal.hpp>

namespace py = pybind11;

void init_signal(py::module m_parent)
{
    auto m = m_parent.def_submodule("_signal");

    std::string module_name = m.attr("__name__").cast<std::string>();

    py::enum_<Amulet::ConnectionMode> ConnectionMode(m, "ConnectionMode");
    ConnectionMode.value(
        "Direct",
        Amulet::ConnectionMode::Direct,
        "Directly called by the emitter.");
    ConnectionMode.value(
        "Async",
        Amulet::ConnectionMode::Async,
        "Called asynchronously.");
    ConnectionMode.attr("__repr__") = py::cpp_function(
        [module_name, ConnectionMode](const py::object& arg) -> py::str {
            return py::str("{}.{}").format(module_name, ConnectionMode.attr("__str__")(arg));
        },
        py::name("__repr__"),
        py::is_method(ConnectionMode));
}
