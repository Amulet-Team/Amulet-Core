#include <pybind11/pybind11.h>

#include <string>

#include <amulet/utils/signal.py.hpp>
#include <amulet/utils/logging.hpp>

namespace py = pybind11;

void init_logging(py::module m_parent)
{
    auto m = m_parent.def_submodule("logging");

    m.def("unregister_default_log_handler", &Amulet::unregister_default_log_handler);

    Amulet::create_signal_binding<Amulet::Signal<int, std::string>>();
    
    m.def("get_logger", []() -> Amulet::PySignal<int, std::string> { return py::cast(Amulet::logger, py::return_value_policy::reference); });
}
