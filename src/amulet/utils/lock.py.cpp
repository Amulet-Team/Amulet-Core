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
        "This is a custom lock implementation that can be acquired in:\n"
        "1) Unique mode.\n"
        "    - Only one thread can use the resource.\n"
        "    - Blocks until no thread holds the lock\n"
        "    - Stops all other threads acquiring the lock until released.\n"
        "2) Shared read-only mode.\n"
        "    - Multiple threads can read (but not write) the resource at the same time.\n"
        "    - Can be acquired in parallel with read mode.\n"
        "    - Blocks until no thread holds the lock in unique or write mode.\n"
        "    - Stops other threads acquiring in unique and write mode until released.\n"
        "3) Shared read mode.\n"
        "    - This thread may only read but other threads may write in parallel.\n"
        "    - Only thread-safe functions may be called in this mode.\n"
        "    - Can be acquired in parallel with read-only mode or write mode (not at the same time)\n"
        "    - Blocks until no thread holds the lock in unique mode.\n"
        "    - Stops other threads acquiring in unique mode until released.\n"
        "4) Shared read-write mode.\n"
        "    - This thread may read and write in parallel with other reading and writing threads.\n"
        "    - Only thread-safe functions may be called in this mode.\n"
        "    - Can be acquired in parallel with read mode.\n"
        "    - Blocks until no thread holds the lock in unique or read-only mode.\n"
        "    - Stops other threads acquiring in unique and read-only mode until released.\n"
        "The lock is ordered meaning it prioritises older acquires over newer ones.\n"
        "It also supports cancelling waiting through a CancelManager instance.");
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
            "Acquire the lock in unique mode.\n"
            "Blocks until no thread holds the lock.\n"
            "Stops all other threads acquiring the lock until released.\n"
            "\n"
            "With improper use this can lead to a deadlock.\n"
            "Only use this if you know what you are doing. Consider using :meth:`unique` instead\n"
            "\n"
            ":param blocking: Should this block until the lock can be acquired. Default is True.\n"
            "    If false and the lock cannot be acquired on the first try, this returns False.\n"
            ":param timeout: The maximum number of seconds to block for. Has no effect is blocking is False. Default is forever.\n"
            ":param task_manager: A custom object through which acquiring can be cancelled.\n"
            "    This effectively manually triggers timeout.\n"
            "    This is useful for GUIs so that the user can cancel an operation that may otherwise block for a while.\n"
            ":return: True if the lock was acquired otherwise False."));
    OrderedLock.def(
        "release_unique",
        &Amulet::OrderedMutex::unlock,
        py::call_guard<py::gil_scoped_release>(),
        py::doc(
            "Release the lock from unique mode.\n"
            "Must be called by the thread that locked it.\n"
            "\n"
            "Only use this if you know what you are doing. Consider using :meth:`unique` instead\n"));
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
            "A context manager to acquire and release the lock in unique mode.\n"
            "\n"
            ">>> lock: OrderedLock\n"
            ">>> with lock.unique():\n"
            ">>>     # code with lock acquired\n"
            ">>> # the lock will automatically be released here\n"
            "\n"
            "Blocks until no thread holds the lock when entering the context manager.\n"
            "Once acquired stops all other threads acquiring the lock until released.\n"
            "Exiting the context manager releases the lock.\n"
            "\n"
            ":param blocking: Should this block until the lock can be acquired. Default is True.\n"
            "    If false and the lock cannot be acquired on the first try, this raises :class:`LockNotAcquired`.\n"
            ":param timeout: The maximum number of seconds to block for. Has no effect is blocking is False. Default is forever.\n"
            ":param task_manager: A custom object through which acquiring can be cancelled.\n"
            "    This effectively manually triggers timeout.\n"
            "    This is useful for GUIs so that the user can cancel an operation that may otherwise block for a while.\n"
            ":return: contextlib.AbstractContextManager[None]\n"
            ":raises: LockNotAcquired if the lock could not be acquired."));

    OrderedLock.def(
        "acquire_shared_read_only",
        [](Amulet::OrderedMutex& self, bool blocking, double timeout, Amulet::AbstractCancelManager& cancel_manager) {
            if (blocking) {
                if (timeout > 0) {
                    return self.try_lock_shared_read_only_for(std::chrono::duration<double>(timeout), cancel_manager);
                } else {
                    return self.try_lock_shared_read_only_for(std::chrono::years(1), cancel_manager);
                }
            } else {
                return self.try_lock_shared_read_only();
            }
        },
        py::arg("blocking") = true,
        py::arg("timeout") = -1.0,
        py::arg("cancel_manager") = Amulet::VoidCancelManager(),
        py::call_guard<py::gil_scoped_release>(),
        py::doc(
            "Acquires the lock in shared read-only mode.\n"
            "Blocks until no thread holds the lock in unique or write mode.\n"
            "Stops other threads acquiring in unique and write mode until released.\n"
            "\n"
            "With improper use this can lead to a deadlock.\n"
            "Only use this if you know what you are doing. Consider using :meth:`shared_read_only` instead\n"
            "\n"
            ":param blocking: Should this block until the lock can be acquired. Default is True.\n"
            "    If false and the lock cannot be acquired on the first try, this returns False.\n"
            ":param timeout: The maximum number of seconds to block for. Has no effect is blocking is False. Default is forever.\n"
            ":param task_manager: A custom object through which acquiring can be cancelled.\n"
            "    This effectively manually triggers timeout.\n"
            "    This is useful for GUIs so that the user can cancel an operation that may otherwise block for a while.\n"
            ":return: True if the lock was acquired otherwise False."));
    OrderedLock.def(
        "shared_read_only",
        [](Amulet::OrderedMutex& self, bool blocking, double timeout, Amulet::AbstractCancelManager& cancel_manager) {
            return pybind11_extensions::contextlib::make_context_manager<void, std::optional<bool>>(
                [&self, blocking, timeout, &cancel_manager]() -> void {
                    py::gil_scoped_release nogil;
                    auto lock = [&]() {
                        if (blocking) {
                            if (timeout > 0) {
                                return self.try_lock_shared_read_only_for(std::chrono::duration<double>(timeout), cancel_manager);
                            } else {
                                return self.try_lock_shared_read_only_for(std::chrono::years(1), cancel_manager);
                            }
                        } else {
                            return self.try_lock_shared_read_only();
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
            "A context manager to acquire and release the lock in shared read-only mode.\n"
            "\n"
            ">>> lock: OrderedLock\n"
            ">>> with lock.shared_read_only():\n"
            ">>>     # code with lock acquired\n"
            ">>> # the lock will automatically be released here\n"
            "\n"
            "Blocks until no thread holds the lock in unique or write mode when entering the context manager.\n"
            "Once acquired stops other threads acquiring in unique and write mode until released.\n"
            "Exiting the context manager releases the lock.\n"
            "\n"
            "If another thread wants to acquire the lock in unique mode it will block until all threads have finished in\n"
            "shared mode.\n"
            "\n"
            ":param blocking: Should this block until the lock can be acquired. Default is True.\n"
            "    If false and the lock cannot be acquired on the first try, this raises :class:`LockNotAcquired`.\n"
            ":param timeout: The maximum number of seconds to block for. Has no effect is blocking is False. Default is forever.\n"
            ":param task_manager: A custom object through which acquiring can be cancelled.\n"
            "    This effectively manually triggers timeout.\n"
            "    This is useful for GUIs so that the user can cancel an operation that may otherwise block for a while.\n"
            ":return: contextlib.AbstractContextManager[None]\n"
            ":raises: LockNotAcquired if the lock could not be acquired."));

    OrderedLock.def(
        "acquire_shared_read",
        [](Amulet::OrderedMutex& self, bool blocking, double timeout, Amulet::AbstractCancelManager& cancel_manager) {
            if (blocking) {
                if (timeout > 0) {
                    return self.try_lock_shared_read_for(std::chrono::duration<double>(timeout), cancel_manager);
                } else {
                    return self.try_lock_shared_read_for(std::chrono::years(1), cancel_manager);
                }
            } else {
                return self.try_lock_shared_read();
            }
        },
        py::arg("blocking") = true,
        py::arg("timeout") = -1.0,
        py::arg("cancel_manager") = Amulet::VoidCancelManager(),
        py::call_guard<py::gil_scoped_release>(),
        py::doc(
            "Acquires the lock in shared read mode.\n"
            "Blocks until no thread holds the lock in unique mode.\n"
            "Stops other threads acquiring in unique mode until released.\n"
            "\n"
            "With improper use this can lead to a deadlock.\n"
            "Only use this if you know what you are doing. Consider using :meth:`shared_read` instead\n"
            "\n"
            ":param blocking: Should this block until the lock can be acquired. Default is True.\n"
            "    If false and the lock cannot be acquired on the first try, this returns False.\n"
            ":param timeout: The maximum number of seconds to block for. Has no effect is blocking is False. Default is forever.\n"
            ":param task_manager: A custom object through which acquiring can be cancelled.\n"
            "    This effectively manually triggers timeout.\n"
            "    This is useful for GUIs so that the user can cancel an operation that may otherwise block for a while.\n"
            ":return: True if the lock was acquired otherwise False."));
    OrderedLock.def(
        "shared_read",
        [](Amulet::OrderedMutex& self, bool blocking, double timeout, Amulet::AbstractCancelManager& cancel_manager) {
            return pybind11_extensions::contextlib::make_context_manager<void, std::optional<bool>>(
                [&self, blocking, timeout, &cancel_manager]() -> void {
                    py::gil_scoped_release nogil;
                    auto lock = [&]() {
                        if (blocking) {
                            if (timeout > 0) {
                                return self.try_lock_shared_read_for(std::chrono::duration<double>(timeout), cancel_manager);
                            } else {
                                return self.try_lock_shared_read_for(std::chrono::years(1), cancel_manager);
                            }
                        } else {
                            return self.try_lock_shared_read();
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
            "A context manager to acquire and release the lock in shared read mode.\n"
            "\n"
            ">>> lock: OrderedLock\n"
            ">>> with lock.shared():\n"
            ">>>     # code with lock acquired\n"
            ">>> # the lock will automatically be released here\n"
            "\n"
            "Blocks until no thread holds the lock in unique mode when entering the context manager.\n"
            "Once acquired stops other threads acquiring in unique mode until released.\n"
            "Exiting the context manager releases the lock.\n"
            "\n"
            ":param blocking: Should this block until the lock can be acquired. Default is True.\n"
            "    If false and the lock cannot be acquired on the first try, this raises :class:`LockNotAcquired`.\n"
            ":param timeout: The maximum number of seconds to block for. Has no effect is blocking is False. Default is forever.\n"
            ":param task_manager: A custom object through which acquiring can be cancelled.\n"
            "    This effectively manually triggers timeout.\n"
            "    This is useful for GUIs so that the user can cancel an operation that may otherwise block for a while.\n"
            ":return: contextlib.AbstractContextManager[None]\n"
            ":raises: LockNotAcquired if the lock could not be acquired."));

    OrderedLock.def(
        "acquire_shared_read_write",
        [](Amulet::OrderedMutex& self, bool blocking, double timeout, Amulet::AbstractCancelManager& cancel_manager) {
            if (blocking) {
                if (timeout > 0) {
                    return self.try_lock_shared_read_write_for(std::chrono::duration<double>(timeout), cancel_manager);
                } else {
                    return self.try_lock_shared_read_write_for(std::chrono::years(1), cancel_manager);
                }
            } else {
                return self.try_lock_shared_read_write();
            }
        },
        py::arg("blocking") = true,
        py::arg("timeout") = -1.0,
        py::arg("cancel_manager") = Amulet::VoidCancelManager(),
        py::call_guard<py::gil_scoped_release>(),
        py::doc(
            "Acquires the lock in shared read-write mode.\n"
            "Blocks until no thread holds the lock in unique or read-only mode.\n"
            "Stops other threads acquiring in unique and read-only mode until released.\n"
            "\n"
            "With improper use this can lead to a deadlock.\n"
            "Only use this if you know what you are doing. Consider using :meth:`shared_read_write` instead\n"
            "\n"
            ":param blocking: Should this block until the lock can be acquired. Default is True.\n"
            "    If false and the lock cannot be acquired on the first try, this returns False.\n"
            ":param timeout: The maximum number of seconds to block for. Has no effect is blocking is False. Default is forever.\n"
            ":param task_manager: A custom object through which acquiring can be cancelled.\n"
            "    This effectively manually triggers timeout.\n"
            "    This is useful for GUIs so that the user can cancel an operation that may otherwise block for a while.\n"
            ":return: True if the lock was acquired otherwise False."));
    OrderedLock.def(
        "shared_read_write",
        [](Amulet::OrderedMutex& self, bool blocking, double timeout, Amulet::AbstractCancelManager& cancel_manager) {
            return pybind11_extensions::contextlib::make_context_manager<void, std::optional<bool>>(
                [&self, blocking, timeout, &cancel_manager]() -> void {
                    py::gil_scoped_release nogil;
                    auto lock = [&]() {
                        if (blocking) {
                            if (timeout > 0) {
                                return self.try_lock_shared_read_write_for(std::chrono::duration<double>(timeout), cancel_manager);
                            } else {
                                return self.try_lock_shared_read_write_for(std::chrono::years(1), cancel_manager);
                            }
                        } else {
                            return self.try_lock_shared_read_write();
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
            "A context manager to acquire and release the lock in shared read-write mode.\n"
            "\n"
            ">>> lock: OrderedLock\n"
            ">>> with lock.shared():\n"
            ">>>     # code with lock acquired\n"
            ">>> # the lock will automatically be released here\n"
            "\n"
            "Blocks until no thread holds the lock in unique or read-only mode when entering the context manager.\n"
            "Once acquired stops other threads acquiring in unique and read-only mode until released.\n"
            "Exiting the context manager releases the lock.\n"
            "\n"
            ":param blocking: Should this block until the lock can be acquired. Default is True.\n"
            "    If false and the lock cannot be acquired on the first try, this raises :class:`LockNotAcquired`.\n"
            ":param timeout: The maximum number of seconds to block for. Has no effect is blocking is False. Default is forever.\n"
            ":param task_manager: A custom object through which acquiring can be cancelled.\n"
            "    This effectively manually triggers timeout.\n"
            "    This is useful for GUIs so that the user can cancel an operation that may otherwise block for a while.\n"
            ":return: contextlib.AbstractContextManager[None]\n"
            ":raises: LockNotAcquired if the lock could not be acquired."));

    OrderedLock.def(
        "release_shared",
        &Amulet::OrderedMutex::unlock_shared,
        py::call_guard<py::gil_scoped_release>(),
        py::doc(
            "Release the lock from any shared mode.\n"
            "Must be called by the thread that locked it.\n"
            "\n"
            "Only use this if you know what you are doing. Consider using :meth:`unique` instead\n"));

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
