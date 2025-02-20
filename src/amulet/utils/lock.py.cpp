// This is a lock class with a similar API to threading.Lock
// It is built on top of Amulet::OrderedMutex
// In C++ code std::unique_lock and std::shared_lock should be used instead of this.
// They aren't particuarly pythonic hence this class existing.

#include <pybind11/pybind11.h>

#include <chrono>
#include <memory>
#include <mutex>
#include <optional>
#include <shared_mutex>
#include <stdexcept>

#include <pybind11_extensions/contextlib.hpp>
#include <pybind11_extensions/py_module.hpp>
#include <pybind11_extensions/pybind11.hpp>

#include "mutex.hpp"
#include "task_manager/cancel_manager.hpp"

namespace py = pybind11;

namespace Amulet {

class LockNotAcquired : public std::runtime_error {
    using std::runtime_error::runtime_error;
};

} // namespace Amulet

static bool acquire_mutex(
    Amulet::OrderedMutex& self,
    bool blocking,
    double timeout,
    Amulet::AbstractCancelManager& cancel_manager,
    const std::pair<Amulet::CurrentThreadMode, Amulet::OtherThreadMode>& thread_mode)
{
    switch (thread_mode.first) {
    case Amulet::CurrentThreadMode::Read:
        switch (thread_mode.second) {
        case Amulet::OtherThreadMode::Null:
            if (blocking) {
                if (0 < timeout) {
                    return self.try_lock_for<Amulet::CurrentThreadMode::Read, Amulet::OtherThreadMode::Null>(std::chrono::duration<double>(timeout), cancel_manager);
                } else {
                    return self.try_lock_for<Amulet::CurrentThreadMode::Read, Amulet::OtherThreadMode::Null>(std::chrono::years(1), cancel_manager);
                }
            } else {
                return self.try_lock<Amulet::CurrentThreadMode::Read, Amulet::OtherThreadMode::Null>();
            }
        case Amulet::OtherThreadMode::Read:
            if (blocking) {
                if (0 < timeout) {
                    return self.try_lock_for<Amulet::CurrentThreadMode::Read, Amulet::OtherThreadMode::Read>(std::chrono::duration<double>(timeout), cancel_manager);
                } else {
                    return self.try_lock_for<Amulet::CurrentThreadMode::Read, Amulet::OtherThreadMode::Read>(std::chrono::years(1), cancel_manager);
                }
            } else {
                return self.try_lock<Amulet::CurrentThreadMode::Read, Amulet::OtherThreadMode::Read>();
            }
        case Amulet::OtherThreadMode::ReadWrite:
            if (blocking) {
                if (0 < timeout) {
                    return self.try_lock_for<Amulet::CurrentThreadMode::Read, Amulet::OtherThreadMode::ReadWrite>(std::chrono::duration<double>(timeout), cancel_manager);
                } else {
                    return self.try_lock_for<Amulet::CurrentThreadMode::Read, Amulet::OtherThreadMode::ReadWrite>(std::chrono::years(1), cancel_manager);
                }
            } else {
                return self.try_lock<Amulet::CurrentThreadMode::Read, Amulet::OtherThreadMode::ReadWrite>();
            }
        }
    case Amulet::CurrentThreadMode::ReadWrite:
        switch (thread_mode.second) {
        case Amulet::OtherThreadMode::Null:
            if (blocking) {
                if (0 < timeout) {
                    return self.try_lock_for<Amulet::CurrentThreadMode::ReadWrite, Amulet::OtherThreadMode::Null>(std::chrono::duration<double>(timeout), cancel_manager);
                } else {
                    return self.try_lock_for<Amulet::CurrentThreadMode::ReadWrite, Amulet::OtherThreadMode::Null>(std::chrono::years(1), cancel_manager);
                }
            } else {
                return self.try_lock<Amulet::CurrentThreadMode::ReadWrite, Amulet::OtherThreadMode::Null>();
            }
        case Amulet::OtherThreadMode::Read:
            if (blocking) {
                if (0 < timeout) {
                    return self.try_lock_for<Amulet::CurrentThreadMode::ReadWrite, Amulet::OtherThreadMode::Read>(std::chrono::duration<double>(timeout), cancel_manager);
                } else {
                    return self.try_lock_for<Amulet::CurrentThreadMode::ReadWrite, Amulet::OtherThreadMode::Read>(std::chrono::years(1), cancel_manager);
                }
            } else {
                return self.try_lock<Amulet::CurrentThreadMode::ReadWrite, Amulet::OtherThreadMode::Read>();
            }
        case Amulet::OtherThreadMode::ReadWrite:
            if (blocking) {
                if (0 < timeout) {
                    return self.try_lock_for<Amulet::CurrentThreadMode::ReadWrite, Amulet::OtherThreadMode::ReadWrite>(std::chrono::duration<double>(timeout), cancel_manager);
                } else {
                    return self.try_lock_for<Amulet::CurrentThreadMode::ReadWrite, Amulet::OtherThreadMode::ReadWrite>(std::chrono::years(1), cancel_manager);
                }
            } else {
                return self.try_lock<Amulet::CurrentThreadMode::ReadWrite, Amulet::OtherThreadMode::ReadWrite>();
            }
        }
    }
    throw std::runtime_error("This should be unreachable.");
}

void init_lock(py::module m_parent)
{
    auto m = m_parent.def_submodule("lock");

    std::string module_name = m.attr("__name__").cast<std::string>();

    auto Deadlock = py::register_exception<Amulet::Deadlock>(m, "Deadlock", PyExc_RuntimeError);
    Deadlock.doc() = "This exception signals that a deadlock occurred when locking a lock.\n"
                     "Not all deadlock cases raise an exception.";

    auto LockNotAcquired = py::register_exception<Amulet::LockNotAcquired>(m, "LockNotAcquired", PyExc_RuntimeError);
    LockNotAcquired.doc() = "An exception raised if the lock was not acquired.";

    py::enum_<Amulet::CurrentThreadMode> CurrentThreadMode(m, "CurrentThreadMode");
    CurrentThreadMode.value(
        "Read",
        Amulet::CurrentThreadMode::Read,
        "This thread can only read.");
    CurrentThreadMode.value(
        "ReadWrite",
        Amulet::CurrentThreadMode::ReadWrite,
        "This thread can read and write.");
    CurrentThreadMode.attr("__repr__") = py::cpp_function(
        [module_name, CurrentThreadMode](const py::object& arg) -> py::str {
            return py::str("{}.{}").format(module_name, CurrentThreadMode.attr("__str__")(arg));
        },
        py::name("__repr__"),
        py::is_method(CurrentThreadMode));

    py::enum_<Amulet::OtherThreadMode> OtherThreadMode(m, "OtherThreadMode");
    OtherThreadMode.value(
        "Null",
        Amulet::OtherThreadMode::Null,
        "Other threads can't do anything.");
    OtherThreadMode.value(
        "Read",
        Amulet::OtherThreadMode::Read,
        "Other threads can only read.");
    OtherThreadMode.value(
        "ReadWrite",
        Amulet::OtherThreadMode::ReadWrite,
        "Other threads can read and write.");
    OtherThreadMode.attr("__repr__") = py::cpp_function(
        [module_name, OtherThreadMode](const py::object& arg) -> py::str {
            return py::str("{}.{}").format(module_name, OtherThreadMode.attr("__str__")(arg));
        },
        py::name("__repr__"),
        py::is_method(OtherThreadMode));

    py::class_<Amulet::OrderedMutex> OrderedLock(m, "OrderedLock",
        "This is a custom mutex implementation that prioritises acquisition order and allows parallelism where possible.\n"
        "The acquirer can define the required permissions for this thread and permissions for other parallel threads.\n"
        "It also supports cancelling waiting through a CancelManager instance.");

    OrderedLock.def(py::init<>());
    OrderedLock.def(
        "acquire",
        &acquire_mutex,
        py::arg("blocking") = true,
        py::arg("timeout") = -1.0,
        py::arg("cancel_manager") = Amulet::VoidCancelManager(),
        py::arg("thread_mode") = std::make_pair(Amulet::CurrentThreadMode::ReadWrite, Amulet::OtherThreadMode::Null),
        py::call_guard<py::gil_scoped_release>(),
        py::doc(
            "Acquire the lock.\n"
            "Stops all other threads acquiring the lock until released.\n"
            "\n"
            "With improper use this can lead to a deadlock.\n"
            "Only use this if you know what you are doing. Consider using the context manager instead\n"
            "\n"
            ":param blocking: Should this block until the lock can be acquired. Default is True.\n"
            "    If false and the lock cannot be acquired on the first try, this returns False.\n"
            ":param timeout: The maximum number of seconds to block for. Has no effect is blocking is False. Default is forever.\n"
            ":param task_manager: A custom object through which acquiring can be cancelled.\n"
            "    This effectively manually triggers timeout.\n"
            "    This is useful for GUIs so that the user can cancel an operation that may otherwise block for a while.\n"
            ":param thread_mode: The permissions for the current and other parallel threads.\n"
            ":return: True if the lock was acquired otherwise False."));
    OrderedLock.def(
        "release",
        &Amulet::OrderedMutex::unlock,
        py::call_guard<py::gil_scoped_release>(),
        py::doc(
            "Release the lock.\n"
            "Must be called by the thread that locked it.\n"
            "\n"
            "Only use this if you know what you are doing. Consider using the context manager instead\n"));
    OrderedLock.def(
        "__call__",
        [](
            Amulet::OrderedMutex& self,
            bool blocking,
            double timeout,
            Amulet::AbstractCancelManager& cancel_manager,
            const std::pair<Amulet::CurrentThreadMode, Amulet::OtherThreadMode>& thread_mode) {
            return pybind11_extensions::contextlib::make_context_manager<void, std::optional<bool>>(
                [&self, blocking, timeout, &cancel_manager, thread_mode]() -> void {
                    py::gil_scoped_release nogil;
                    if (!acquire_mutex(self, blocking, timeout, cancel_manager, thread_mode)) {
                        throw Amulet::LockNotAcquired("Lock was not acquired.");
                    }
                },
                [&self](py::object, py::object, py::object) -> std::optional<bool> {
                    py::gil_scoped_release nogil;
                    self.unlock();
                    return false;
                });
        },
        py::arg("blocking") = true,
        py::arg("timeout") = -1.0,
        py::arg("cancel_manager") = Amulet::VoidCancelManager(),
        py::arg("thread_mode") = std::make_pair(Amulet::CurrentThreadMode::ReadWrite, Amulet::OtherThreadMode::Null),
        py::keep_alive<0, 1>(),
        py::keep_alive<0, 4>(),
        py::doc(
            "A context manager to acquire and release the lock.\n"
            "\n"
            ">>> lock: OrderedLock\n"
            ">>> with lock():\n"
            ">>>     # code with lock acquired\n"
            ">>> # the lock will automatically be released here\n"
            "\n"
            "Blocks until no thread holds the lock when entering the context manager.\n"
            "Once acquired, stops all other threads acquiring the lock until released.\n"
            "Exiting the context manager releases the lock.\n"
            "\n"
            ":param blocking: Should this block until the lock can be acquired. Default is True.\n"
            "    If false and the lock cannot be acquired on the first try, this raises :class:`LockNotAcquired`.\n"
            ":param timeout: The maximum number of seconds to block for. Has no effect is blocking is False. Default is forever.\n"
            ":param task_manager: A custom object through which acquiring can be cancelled.\n"
            "    This effectively manually triggers timeout.\n"
            "    This is useful for GUIs so that the user can cancel an operation that may otherwise block for a while.\n"
            ":param thread_mode: The permissions for the current and other parallel threads.\n"
            ":return: contextlib.AbstractContextManager[None]\n"
            ":raises: LockNotAcquired if the lock could not be acquired."));

    py::class_<std::mutex> Lock(m, "Lock", py::module_local(),
        "A wrapper for std::mutex.");
    Lock.def(py::init());
    Lock.def(
        "__enter__",
        &std::mutex::lock,
        py::call_guard<py::gil_scoped_release>());
    Lock.def(
        "__exit__",
        [](std::mutex& self, py::object, py::object, py::object) {
            py::gil_scoped_release nogil;
            self.unlock();
        },
        py::arg("exc_type"),
        py::arg("exc_val"),
        py::arg("exc_tb"));
    Lock.def(
        "acquire",
        [](std::mutex& self, bool blocking) {
            if (blocking) {
                self.lock();
                return true;
            } else {
                return self.try_lock();
            }
        },
        py::arg("blocking") = true,
        py::call_guard<py::gil_scoped_release>());
    Lock.def(
        "release",
        &std::mutex::unlock,
        py::call_guard<py::gil_scoped_release>());

    py::class_<std::recursive_mutex> RLock(m, "RLock", py::module_local(),
        "A wrapper for std::recursive_mutex.");
    RLock.def(py::init());
    RLock.def(
        "__enter__",
        &std::recursive_mutex::lock,
        py::call_guard<py::gil_scoped_release>());
    RLock.def(
        "__exit__",
        [](std::recursive_mutex& self, py::object, py::object, py::object) {
            py::gil_scoped_release nogil;
            self.unlock();
        },
        py::arg("exc_type"),
        py::arg("exc_val"),
        py::arg("exc_tb"));
    RLock.def(
        "acquire",
        [](std::recursive_mutex& self, bool blocking) {
            if (blocking) {
                self.lock();
                return true;
            } else {
                return self.try_lock();
            }
        },
        py::arg("blocking") = true,
        py::call_guard<py::gil_scoped_release>());
    RLock.def(
        "release",
        &std::recursive_mutex::unlock,
        py::call_guard<py::gil_scoped_release>());

    py::class_<std::shared_mutex> SharedLock(m, "SharedLock", py::module_local(),
        "A wrapper for std::shared_mutex.");
    SharedLock.def(py::init());
    SharedLock.def(
        "acquire_unique",
        [](std::shared_mutex& self, bool blocking) {
            if (blocking) {
                self.lock();
                return true;
            } else {
                return self.try_lock();
            }
        },
        py::arg("blocking") = true,
        py::call_guard<py::gil_scoped_release>());
    SharedLock.def(
        "release_unique",
        &std::shared_mutex::unlock,
        py::call_guard<py::gil_scoped_release>());
    SharedLock.def(
        "unique",
        [](std::shared_mutex& self) {
            return pybind11_extensions::contextlib::make_context_manager<void, std::optional<bool>>(
                [&self]() -> void {
                    py::gil_scoped_release nogil;
                    self.lock();
                },
                [&self](py::object, py::object, py::object) -> std::optional<bool> {
                    py::gil_scoped_release nogil;
                    self.unlock();
                    return false;
                });
        },
        py::keep_alive<0, 1>());
    SharedLock.def(
        "acquire_shared",
        [](std::shared_mutex& self, bool blocking) {
            if (blocking) {
                self.lock_shared();
                return true;
            } else {
                return self.try_lock_shared();
            }
        },
        py::arg("blocking") = true,
        py::call_guard<py::gil_scoped_release>());
    SharedLock.def(
        "release_shared",
        &std::shared_mutex::unlock_shared,
        py::call_guard<py::gil_scoped_release>());
    SharedLock.def(
        "shared",
        [](std::shared_mutex& self) {
            return pybind11_extensions::contextlib::make_context_manager<void, std::optional<bool>>(
                [&self]() -> void {
                    py::gil_scoped_release nogil;
                    self.lock_shared();
                },
                [&self](py::object, py::object, py::object) -> std::optional<bool> {
                    py::gil_scoped_release nogil;
                    self.unlock_shared();
                    return false;
                });
        },
        py::keep_alive<0, 1>());
}
