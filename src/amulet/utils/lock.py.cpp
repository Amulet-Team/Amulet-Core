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

void init_lock(py::module m_parent)
{
    auto m = m_parent.def_submodule("lock");

    auto Deadlock = py::register_exception<Amulet::Deadlock>(m, "Deadlock", PyExc_RuntimeError);
    Deadlock.doc() = "This exception signals that a deadlock occurred when locking a lock.\n"
                     "Not all deadlock cases raise an exception.";

    auto LockNotAcquired = py::register_exception<Amulet::LockNotAcquired>(m, "LockNotAcquired", PyExc_RuntimeError);
    LockNotAcquired.doc() = "An exception raised if the lock was not acquired.";

    py::class_<Amulet::OrderedMutex> OrderedLock(m, "OrderedLock",
        "This is a custom lock implementation that can be acquired in\n"
        "1) unique mode.\n"
        "    - This is the normal mode where only this thread can use the resource.\n"
        "    - All other acquires block until it is released.\n"
        "2) shared mode.\n"
        "    - This allows multiple threads to acquire the resource at the same time.\n"
        "    - This is useful if multiple threads want to read a resource but not write to it.\n"
        "    - If the resource is locked in unique mode this will block.\n"
        "    - Once locked in shared mode it will block unique acquires until all shared threads release it.\n"
        "Tasks are prioritised in the order the call is made");
    OrderedLock.def(py::init<>());
    OrderedLock.def(
        "acquire_unique",
        [](Amulet::OrderedMutex& self, bool blocking, double timeout, Amulet::AbstractCancelManager& cancel_manager) {
            if (blocking) {
                if (timeout > 0) {
                    return self.try_lock_for(std::chrono::duration<double>(timeout), cancel_manager);
                } else {
                    return self.try_lock_for(std::chrono::years(1), cancel_manager);
                }
            } else {
                return self.try_lock();
            }
        },
        py::arg("blocking") = true,
        py::arg("timeout") = -1.0,
        py::arg("cancel_manager") = Amulet::VoidCancelManager(),
        py::call_guard<py::gil_scoped_release>(),
        py::doc(
            "Only use this if you know what you are doing. Consider using :meth:`unique` instead\n"
            "Acquire the lock in unique mode. This is equivalent to threading.Lock.acquire\n"
            "With improper use this can lead to a deadlock.\n"
            ":param blocking: Should this block until the lock can be acquired. Default is True.\n"
            "    If false and the lock cannot be acquired on the first try, this returns False.\n"
            ":param timeout: Maximum amount of time to block for. Has no effect is blocking is False. Default is forever.\n"
            ":param task_manager: A custom object through which acquiring can be cancelled.\n"
            "    This effectively manually triggers timeout.\n"
            "    This is useful for GUIs so that the user can cancel an operation that may otherwise block for a while.\n"
            ":return: True if the lock was acquired otherwise False."));
    OrderedLock.def(
        "release_unique",
        &Amulet::OrderedMutex::unlock,
        py::call_guard<py::gil_scoped_release>(),
        py::doc(
            "Only use this if you know what you are doing. Consider using :meth:`unique` instead\n"
            "Release the unique hold on the lock. This must be called by the same thread that acquired it.\n"
            "This must be called exactly the same number of times as :meth:`acquire_unique` was called."));
    OrderedLock.def(
        "acquire_shared",
        [](Amulet::OrderedMutex& self, bool blocking, double timeout, Amulet::AbstractCancelManager& cancel_manager) {
            if (blocking) {
                if (timeout > 0) {
                    return self.try_lock_shared_for(std::chrono::duration<double>(timeout), cancel_manager);
                } else {
                    return self.try_lock_shared_for(std::chrono::years(1), cancel_manager);
                }
            } else {
                return self.try_lock_shared();
            }
        },
        py::arg("blocking") = true,
        py::arg("timeout") = -1.0,
        py::arg("cancel_manager") = Amulet::VoidCancelManager(),
        py::call_guard<py::gil_scoped_release>(),
        py::doc(
            "Only use this if you know what you are doing. Consider using :meth:`shared` instead\n"
            "Acquire the lock in shared mode.\n"
            ":param blocking: Should this block until the lock can be acquired. Default is True.\n"
            "    If false and the lock cannot be acquired on the first try, this returns False.\n"
            ":param timeout: Maximum amount of time to block for. Has no effect is blocking is False. Default is forever.\n"
            ":param task_manager: A custom object through which acquiring can be cancelled.\n"
            "    This effectively manually triggers timeout.\n"
            "    This is useful for GUIs so that the user can cancel an operation that may otherwise block for a while.\n"
            ":return: True if the lock was acquired otherwise False."));
    OrderedLock.def(
        "release_shared",
        &Amulet::OrderedMutex::unlock_shared,
        py::call_guard<py::gil_scoped_release>(),
        py::doc(
            "Only use this if you know what you are doing. Consider using :meth:`shared` instead\n"
            "Release the shared hold on the lock. This must be called by the same thread that acquired it.\n"
            "This must be called exactly the same number of times as :meth:`acquire_shared` was called."));
    OrderedLock.def(
        "unique",
        [](Amulet::OrderedMutex& self, bool blocking, double timeout, Amulet::AbstractCancelManager& cancel_manager) {
            return pybind11_extensions::contextlib::make_context_manager<void, std::optional<bool>>(
                [&self, blocking, timeout, &cancel_manager]() -> void {
                    py::gil_scoped_release nogil;
                    auto lock = [&]() {
                        if (blocking) {
                            if (timeout > 0) {
                                return self.try_lock_for(std::chrono::duration<double>(timeout), cancel_manager);
                            } else {
                                return self.try_lock_for(std::chrono::years(1), cancel_manager);
                            }
                        } else {
                            return self.try_lock();
                        }
                    };
                    if (!lock()) {
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
        py::keep_alive<0, 1>(),
        py::keep_alive<0, 4>(),
        py::doc(
            "Acquire the lock in unique mode.\n"
            "This is used as follows\n"
            "\n"
            ">>> lock: OrderedLock\n"
            ">>> with lock.unique():\n"
            ">>>     # code with lock acquired\n"
            ">>> # the lock will automatically be released here\n"
            "\n"
            "This will block while all other threads using the resource finish\n"
            "and once acquired block all other threads until the lock is released.\n"
            "\n"
            ":param blocking: Should this block until the lock can be acquired. Default is True.\n"
            "    If false and the lock cannot be acquired on the first try, this returns False.\n"
            ":param timeout: Maximum amount of time to block for. Has no effect is blocking is False. Default is forever.\n"
            ":param task_manager: A custom object through which acquiring can be cancelled.\n"
            "    This effectively manually triggers timeout.\n"
            "    This is useful for GUIs so that the user can cancel an operation that may otherwise block for a while.\n"
            ":return: None\n"
            ":raises: LockNotAcquired if the lock could not be acquired."));
    OrderedLock.def(
        "shared",
        [](Amulet::OrderedMutex& self, bool blocking, double timeout, Amulet::AbstractCancelManager& cancel_manager) {
            return pybind11_extensions::contextlib::make_context_manager<void, std::optional<bool>>(
                [&self, blocking, timeout, &cancel_manager]() -> void {
                    py::gil_scoped_release nogil;
                    auto lock = [&]() {
                        if (blocking) {
                            if (timeout > 0) {
                                return self.try_lock_shared_for(std::chrono::duration<double>(timeout), cancel_manager);
                            } else {
                                return self.try_lock_shared_for(std::chrono::years(1), cancel_manager);
                            }
                        } else {
                            return self.try_lock_shared();
                        }
                    };
                    if (!lock()) {
                        throw Amulet::LockNotAcquired("Lock was not acquired.");
                    }
                },
                [&self](py::object, py::object, py::object) -> std::optional<bool> {
                    py::gil_scoped_release nogil;
                    self.unlock_shared();
                    return false;
                });
        },
        py::arg("blocking") = true,
        py::arg("timeout") = -1.0,
        py::arg("cancel_manager") = Amulet::VoidCancelManager(),
        py::keep_alive<0, 1>(),
        py::keep_alive<0, 4>(),
        py::doc(
            "Acquire the lock in shared mode.\n"
            "This is used as follows\n"
            "\n"
            ">>> lock: OrderedLock\n"
            ">>> with lock.shared():\n"
            ">>>     # code with lock acquired\n"
            ">>> # the lock will automatically be released here\n"
            "\n"
            "If the lock is acquired by a different thread in unique mode then this will block until it is finished.\n"
            "If the lock is acquired in unique mode by this thread or by other threads in shared mode then this will acquire\n"
            "the lock.\n"
            "\n"
            "If another thread wants to acquire the lock in unique mode it will block until all threads have finished in\n"
            "shared mode.\n"
            "\n"
            ":param blocking: Should this block until the lock can be acquired. Default is True.\n"
            "    If false and the lock cannot be acquired on the first try, this returns False.\n"
            ":param timeout: Maximum amount of time to block for. Has no effect is blocking is False. Default is forever.\n"
            ":param task_manager: A custom object through which acquiring can be cancelled.\n"
            "    This effectively manually triggers timeout.\n"
            "    This is useful for GUIs so that the user can cancel an operation that may otherwise block for a while.\n"
            ":return: None\n"
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
