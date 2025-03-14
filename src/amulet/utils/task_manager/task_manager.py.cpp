#include <pybind11/functional.h>
#include <pybind11/pybind11.h>

#include <string>

#include <pybind11_extensions/py_module.hpp>

#include <amulet/utils/signal.py.hpp>

#include "cancel_manager.hpp"
#include "progress_manager.hpp"

namespace py = pybind11;

static py::module init_cancel_manager(py::module m_parent)
{
    auto m = m_parent.def_submodule("cancel_manager");

    std::string module_name = m.attr("__name__").cast<std::string>();

    py::register_exception<Amulet::TaskCancelled>(m, "TaskCancelled");

    Amulet::create_signal_binding<Amulet::Signal<>>();
    Amulet::create_signal_binding<Amulet::Signal<float>>();
    Amulet::create_signal_binding<Amulet::Signal<std::string>>();

    py::class_<Amulet::AbstractCancelManager> AbstractCancelManager(m, "AbstractCancelManager");
    AbstractCancelManager.def(
        "cancel",
        &Amulet::AbstractCancelManager::cancel,
        py::doc("Request the operation be cancelled.\n"
                "It is down to the operation to implement support for this."));
    AbstractCancelManager.def(
        "is_cancel_requested",
        &Amulet::AbstractCancelManager::is_cancel_requested,
        py::doc("Has :meth:`cancel` been called to signal that the operation should be cancelled."));
    AbstractCancelManager.def(
        "register_cancel_callback",
        [](Amulet::AbstractCancelManager& self, Amulet::CancelCallback callback) -> Amulet::PySignalToken<> {
            return py::cast(self.register_cancel_callback(std::move(callback)), py::return_value_policy::move);
        },
        py::arg("callback"),
        py::doc("Register a function to get called when cancel is called.\n"
                "The callback will be called from the thread `cancel` is called in."));
    AbstractCancelManager.def(
        "unregister_cancel_callback",
        [](Amulet::AbstractCancelManager& self, Amulet::PySignalToken<> token) {
            return self.unregister_cancel_callback(token.cast<Amulet::SignalToken<>>());
        },
        py::arg("token"),
        py::doc("Unregister a registered function from being called when cancel is called."));

    py::class_<Amulet::VoidCancelManager, Amulet::AbstractCancelManager> VoidCancelManager(m, "VoidCancelManager");
    VoidCancelManager.def(py::init<>());
    VoidCancelManager.def(
        "__repr__",
        [module_name](const Amulet::VoidCancelManager&) { return module_name + ".VoidCancelManager()"; });

    py::class_<Amulet::CancelManager, Amulet::AbstractCancelManager> CancelManager(m, "CancelManager");
    CancelManager.def(py::init<>());
    CancelManager.def(
        "__repr__",
        [module_name](const Amulet::CancelManager&) { return module_name + ".CancelManager()"; });

    return m;
}

static py::module init_progress_manager(py::module m_parent)
{
    auto m = m_parent.def_submodule("progress_manager");

    std::string module_name = m.attr("__name__").cast<std::string>();

    py::class_<Amulet::AbstractProgressManager> AbstractProgressManager(m, "AbstractProgressManager");
    AbstractProgressManager.def(
        "register_progress_callback",
        [](Amulet::AbstractProgressManager& self, Amulet::ProgressCallback callback) -> Amulet::PySignalToken<float> {
            return py::cast(self.register_progress_callback(std::move(callback)), py::return_value_policy::move);
        },
        py::arg("callback"));
    AbstractProgressManager.def(
        "unregister_progress_callback",
        [](Amulet::AbstractProgressManager& self, Amulet::PySignalToken<float> token) {
            return self.unregister_progress_callback(token.cast<Amulet::SignalToken<float>>());
        },
        py::arg("token"));
    AbstractProgressManager.def(
        "update_progress",
        &Amulet::AbstractProgressManager::update_progress,
        py::arg("progress"));
    AbstractProgressManager.def(
        "register_progress_text_callback",
        [](Amulet::AbstractProgressManager& self, Amulet::ProgressTextCallback callback) -> Amulet::PySignalToken<std::string> {
            return py::cast(self.register_progress_text_callback(std::move(callback)), py::return_value_policy::move);
        },
        py::arg("callback"));
    AbstractProgressManager.def(
        "unregister_progress_text_callback",
        [](Amulet::AbstractProgressManager& self, Amulet::PySignalToken<std::string> token) {
            return self.unregister_progress_text_callback(token.cast<Amulet::SignalToken<std::string>>());
        },
        py::arg("token"));
    AbstractProgressManager.def(
        "update_progress_text",
        &Amulet::AbstractProgressManager::update_progress_text,
        py::arg("text"));
    AbstractProgressManager.def(
        "get_child",
        &Amulet::AbstractProgressManager::get_child,
        py::arg("progress_min"),
        py::arg("progress_max"));

    py::class_<Amulet::VoidProgressManager, Amulet::AbstractProgressManager> VoidProgressManager(m, "VoidProgressManager");
    VoidProgressManager.def(py::init<>());
    VoidProgressManager.def(
        "__repr__",
        [module_name](const Amulet::VoidProgressManager&) { return module_name + ".VoidProgressManager()"; });

    py::class_<Amulet::ProgressManager, Amulet::AbstractProgressManager> ProgressManager(m, "ProgressManager");
    ProgressManager.def(py::init<>());
    ProgressManager.def(
        "__repr__",
        [module_name](const Amulet::ProgressManager&) { return module_name + ".ProgressManager()"; });

    return m;
}

void init_task_manager(py::module m_parent)
{
    auto m = pybind11_extensions::def_subpackage(m_parent, "task_manager");
    auto m_cancel = init_cancel_manager(m);
    auto m_progress = init_progress_manager(m);

    m.attr("TaskCancelled") = m_cancel.attr("TaskCancelled");
    m.attr("AbstractCancelManager") = m_cancel.attr("AbstractCancelManager");
    m.attr("VoidCancelManager") = m_cancel.attr("VoidCancelManager");
    m.attr("CancelManager") = m_cancel.attr("CancelManager");

    m.attr("AbstractProgressManager") = m_progress.attr("AbstractProgressManager");
    m.attr("VoidProgressManager") = m_progress.attr("VoidProgressManager");
    m.attr("ProgressManager") = m_progress.attr("ProgressManager");
}
