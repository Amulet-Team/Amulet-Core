// This is a lock class with a similar API to threading.Lock
// It is built on top of Amulet::OrderedSharedTimedMutex
// In C++ code std::unique_lock and std::shared_lock should be used instead of this.
// They aren't particuarly pythonic hence this class existing.

#include <pybind11/pybind11.h>

#include <chrono>
#include <memory>
#include <stdexcept>

#include <pybind11_extensions/py_module.hpp>

#include "mutex.hpp"
#include "task_manager/cancel_manager.hpp"

namespace py = pybind11;

namespace Amulet {

class LockNotAcquired : public std::runtime_error {
    using std::runtime_error::runtime_error;
};

class OrderedSharedLock;

class UniqueLockContextManager {
private:
    OrderedSharedLock& lock;
    bool blocking;
    double timeout;
    AbstractCancelManager& cancel_manager;

public:
    UniqueLockContextManager(
        OrderedSharedLock& lock,
        bool blocking,
        double timeout,
        AbstractCancelManager& cancel_manager);
    void enter();
    void exit();
};

class SharedLockContextManager {
    OrderedSharedLock& lock;
    bool blocking;
    double timeout;
    AbstractCancelManager& cancel_manager;

public:
    SharedLockContextManager(
        OrderedSharedLock& lock,
        bool blocking,
        double timeout,
        AbstractCancelManager& cancel_manager);
    void enter();
    void exit();
};

class OrderedSharedLock {
    // Will be a nullptr if constructed from a reference
    std::unique_ptr<OrderedSharedTimedMutex> _mutex_storage;
    OrderedSharedTimedMutex& _mutex;

public:
    OrderedSharedLock(OrderedSharedTimedMutex& mutex);
    OrderedSharedLock(std::unique_ptr<OrderedSharedTimedMutex> mutex);
    OrderedSharedLock();
    bool acquire_unique(
        bool blocking = true,
        double timeout = -1,
        AbstractCancelManager& cancel_manager = global_VoidCancelManager);
    void release_unique();
    bool acquire_shared(
        bool blocking = true,
        double timeout = -1,
        AbstractCancelManager& cancel_manager = global_VoidCancelManager);
    void release_shared();
    UniqueLockContextManager unique(
        bool blocking = true,
        double timeout = -1,
        AbstractCancelManager& cancel_manager = global_VoidCancelManager);
    SharedLockContextManager shared(
        bool blocking = true,
        double timeout = -1,
        AbstractCancelManager& cancel_manager = global_VoidCancelManager);
};

UniqueLockContextManager::UniqueLockContextManager(
    OrderedSharedLock& lock,
    bool blocking,
    double timeout,
    AbstractCancelManager& cancel_manager)
    : lock(lock)
    , blocking(blocking)
    , timeout(timeout)
    , cancel_manager(cancel_manager)
{
}
void UniqueLockContextManager::enter()
{
    if (!lock.acquire_unique(blocking, timeout, cancel_manager)) {
        throw LockNotAcquired("Lock was not acquired.");
    }
}
void UniqueLockContextManager::exit()
{
    lock.release_unique();
}

SharedLockContextManager::SharedLockContextManager(
    OrderedSharedLock& lock,
    bool blocking,
    double timeout,
    AbstractCancelManager& cancel_manager)
    : lock(lock)
    , blocking(blocking)
    , timeout(timeout)
    , cancel_manager(cancel_manager)
{
}
void SharedLockContextManager::enter()
{
    if (!lock.acquire_shared(blocking, timeout, cancel_manager)) {
        throw LockNotAcquired("Lock was not acquired.");
    }
}
void SharedLockContextManager::exit()
{
    lock.release_shared();
}

// Construct from reference
OrderedSharedLock::OrderedSharedLock(OrderedSharedTimedMutex& mutex)
    : _mutex(mutex)
{
}
// Construct from unique_ptr
OrderedSharedLock::OrderedSharedLock(std::unique_ptr<OrderedSharedTimedMutex> mutex)
    : _mutex_storage(std::move(mutex))
    , _mutex(*_mutex_storage)
{
}
// Default constructor
OrderedSharedLock::OrderedSharedLock()
    : OrderedSharedLock(std::make_unique<OrderedSharedTimedMutex>())
{
}
bool OrderedSharedLock::acquire_unique(
    bool blocking,
    double timeout,
    AbstractCancelManager& cancel_manager)
{
    if (blocking) {
        if (timeout > 0) {
            return _mutex.try_lock_for(std::chrono::duration<double>(timeout), cancel_manager);
        } else {
            return _mutex.try_lock_for(std::chrono::years(1), cancel_manager);
        }
    } else {
        return _mutex.try_lock();
    }
}
void OrderedSharedLock::release_unique()
{
    _mutex.unlock();
}
bool OrderedSharedLock::acquire_shared(
    bool blocking,
    double timeout,
    AbstractCancelManager& cancel_manager)
{
    if (blocking) {
        if (timeout > 0) {
            return _mutex.try_lock_shared_for(std::chrono::duration<double>(timeout), cancel_manager);
        } else {
            return _mutex.try_lock_shared_for(std::chrono::years(1), cancel_manager);
        }
    } else {
        return _mutex.try_lock_shared();
    }
}
void OrderedSharedLock::release_shared()
{
    _mutex.unlock_shared();
}
UniqueLockContextManager OrderedSharedLock::unique(
    bool blocking,
    double timeout,
    AbstractCancelManager& cancel_manager)
{
    return { *this, blocking, timeout, cancel_manager };
}
SharedLockContextManager OrderedSharedLock::shared(
    bool blocking,
    double timeout,
    AbstractCancelManager& cancel_manager)
{
    return { *this, blocking, timeout, cancel_manager };
}

} // namespace Amulet

void init_lock(py::module m_parent)
{
    auto m = m_parent.def_submodule("lock");

    auto LockNotAcquired = py::register_exception<Amulet::LockNotAcquired>(m, "LockNotAcquired", PyExc_RuntimeError);
    LockNotAcquired.doc() = "An exception raised if the lock was not acquired.";

    py::class_<Amulet::UniqueLockContextManager> UniqueLockContextManager(m, "UniqueLockContextManager");
    UniqueLockContextManager.def(
        "__enter__",
        &Amulet::UniqueLockContextManager::enter,
        py::call_guard<py::gil_scoped_release>());
    UniqueLockContextManager.def(
        "__exit__",
        [](Amulet::UniqueLockContextManager& self, py::object, py::object, py::object) {
            py::gil_scoped_release gil;
            self.exit();
        });
    py::class_<Amulet::SharedLockContextManager> SharedLockContextManager(m, "SharedLockContextManager");
    SharedLockContextManager.def(
        "__enter__",
        &Amulet::SharedLockContextManager::enter,
        py::call_guard<py::gil_scoped_release>());
    SharedLockContextManager.def(
        "__exit__",
        [](Amulet::SharedLockContextManager& self, py::object, py::object, py::object) {
            py::gil_scoped_release gil;
            self.exit();
        });

    py::class_<Amulet::OrderedSharedLock> OrderedSharedLock(m, "OrderedSharedLock",
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
    OrderedSharedLock.def(
        py::init<Amulet::OrderedSharedTimedMutex&>(),
        py::arg("mutex"),
        py::keep_alive<1, 2>());
    OrderedSharedLock.def(py::init<>());
    OrderedSharedLock.def(
        "acquire_unique",
        &Amulet::OrderedSharedLock::acquire_unique,
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
    OrderedSharedLock.def(
        "release_unique",
        &Amulet::OrderedSharedLock::release_unique,
        py::call_guard<py::gil_scoped_release>(),
        py::doc(
            "Only use this if you know what you are doing. Consider using :meth:`unique` instead\n"
            "Release the unique hold on the lock. This must be called by the same thread that acquired it.\n"
            "This must be called exactly the same number of times as :meth:`acquire_unique` was called."));
    OrderedSharedLock.def(
        "acquire_shared",
        &Amulet::OrderedSharedLock::acquire_shared,
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
    OrderedSharedLock.def(
        "release_shared",
        &Amulet::OrderedSharedLock::release_shared,
        py::call_guard<py::gil_scoped_release>(),
        py::doc(
            "Only use this if you know what you are doing. Consider using :meth:`shared` instead\n"
            "Release the shared hold on the lock. This must be called by the same thread that acquired it.\n"
            "This must be called exactly the same number of times as :meth:`acquire_shared` was called."));
    OrderedSharedLock.def(
        "unique",
        &Amulet::OrderedSharedLock::unique,
        py::arg("blocking") = true,
        py::arg("timeout") = -1.0,
        py::arg("cancel_manager") = Amulet::VoidCancelManager(),
        py::call_guard<py::gil_scoped_release>(),
        py::keep_alive<0, 1>(),
        py::doc(
            "Acquire the lock in unique mode.\n"
            "This is used as follows\n"
            "\n"
            ">>> lock: OrderedSharedLock\n"
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
    OrderedSharedLock.def(
        "shared",
        &Amulet::OrderedSharedLock::shared,
        py::arg("blocking") = true,
        py::arg("timeout") = -1.0,
        py::arg("cancel_manager") = Amulet::VoidCancelManager(),
        py::call_guard<py::gil_scoped_release>(),
        py::keep_alive<0, 1>(),
        py::doc(
            "Acquire the lock in shared mode.\n"
            "This is used as follows\n"
            "\n"
            ">>> lock: OrderedSharedLock\n"
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
}
