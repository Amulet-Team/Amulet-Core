#include <pybind11/pybind11.h>

#include <string>

#include <amulet/utils/logging.hpp>
#include <amulet/utils/signal.py.hpp>

namespace py = pybind11;

void init_logging(py::module m_parent)
{
    auto m = m_parent.def_submodule("logging");

    m.def(
        "register_default_log_handler",
        &Amulet::register_default_log_handler,
        py::doc("Register the default log handler.\n"
                "This is registered by default with a log level of 20.\n"
                "Thread safe."));
    m.def(
        "unregister_default_log_handler",
        &Amulet::unregister_default_log_handler,
        py::doc("Unregister the default log handler.\n"
                "Thread safe."));
    m.def(
        "get_default_log_level",
        &Amulet::get_default_log_level,
        py::doc("Get the log level used by the default logger.\n"
                "The default logger will only log messages with a level at least this large.\n"
                "Thread safe."));
    m.def(
        "set_default_log_level",
        &Amulet::set_default_log_level,
        py::arg("level"),
        py::doc("Set the log level used by the default logger.\n"
                "The default logger will only log messages with a level at least this large.\n"
                "Thread safe."));

    Amulet::create_signal_binding<Amulet::Signal<int, std::string>>();

    m.def(
        "get_logger",
        []() -> Amulet::PySignal<int, std::string> { return py::cast(Amulet::logger, py::return_value_policy::reference); },
        py::doc("Get the logger signal.\n"
                "This is emitted with the message and its level every time a message is logged."));
}
