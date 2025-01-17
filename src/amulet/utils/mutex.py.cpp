#include <memory>

#include <pybind11/pybind11.h>
#include <pybind11/chrono.h>
#include <pybind11_extensions/py_module.hpp>

#include "mutex.hpp"
#include "task_manager/cancel_manager.hpp"

namespace py = pybind11;

void init_mutex(py::module m_parent)
{
    auto m = m_parent.def_submodule("mutex");

    std::string module_name = m.attr("__name__").cast<std::string>();

    py::class_<Amulet::OrderedSharedMutex, std::shared_ptr<Amulet::OrderedSharedMutex>> OrderedSharedMutex(m, "OrderedSharedMutex");
    OrderedSharedMutex.def(py::init<>());
    OrderedSharedMutex.def(
        "lock",
        &Amulet::OrderedSharedMutex::lock,
        py::arg("cancel_manager") = Amulet::VoidCancelManager());
    OrderedSharedMutex.def(
        "try_lock",
        &Amulet::OrderedSharedMutex::try_lock);
    OrderedSharedMutex.def(
        "unlock",
        &Amulet::OrderedSharedMutex::unlock);
    OrderedSharedMutex.def(
        "lock_shared",
        &Amulet::OrderedSharedMutex::lock_shared,
        py::arg("cancel_manager") = Amulet::global_VoidCancelManager);
    OrderedSharedMutex.def(
        "try_lock_shared",
        &Amulet::OrderedSharedMutex::try_lock_shared);
    OrderedSharedMutex.def(
        "unlock_shared",
        &Amulet::OrderedSharedMutex::unlock_shared);
    OrderedSharedMutex.def_static(
        "__repr__",
        [module_name](const Amulet::OrderedSharedMutex&) { return module_name + "OrderedSharedMutex()"; });

    py::class_<Amulet::OrderedSharedTimedMutex, std::shared_ptr<Amulet::OrderedSharedTimedMutex>, Amulet::OrderedSharedMutex> OrderedSharedTimedMutex(m, "OrderedSharedTimedMutex");
    OrderedSharedTimedMutex.def(
        "try_lock_for",
        &Amulet::OrderedSharedTimedMutex::try_lock_for<std::chrono::seconds::rep, std::chrono::seconds::period>,
        py::arg("timeout_duration"),
        py::arg("cancel_manager") = Amulet::global_VoidCancelManager);
    OrderedSharedTimedMutex.def(
        "try_lock_until",
        &Amulet::OrderedSharedTimedMutex::try_lock_until<std::chrono::system_clock, std::chrono::system_clock::duration>,
        py::arg("timeout_time"),
        py::arg("cancel_manager") = Amulet::global_VoidCancelManager);
    OrderedSharedTimedMutex.def(
        "try_lock_shared_for",
        &Amulet::OrderedSharedTimedMutex::try_lock_shared_for<std::chrono::seconds::rep, std::chrono::seconds::period>,
        py::arg("timeout_duration"),
        py::arg("cancel_manager") = Amulet::global_VoidCancelManager);
    OrderedSharedTimedMutex.def(
        "try_lock_shared_until",
        &Amulet::OrderedSharedTimedMutex::try_lock_shared_until<std::chrono::system_clock, std::chrono::system_clock::duration>,
        py::arg("timeout_time"),
        py::arg("cancel_manager") = Amulet::global_VoidCancelManager);
    OrderedSharedTimedMutex.def_static(
        "__repr__",
        [module_name](Amulet::OrderedSharedTimedMutex&) { return module_name + "OrderedSharedTimedMutex()"; });
}
