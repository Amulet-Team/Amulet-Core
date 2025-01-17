// This is a lock class with a similar API to threading.Lock
// It is built on top of Amulet::OrderedSharedTimedMutex
// In C++ code std::unique_lock and std::shared_lock should be used instead of this.
// They aren't particuarly pythonic hence this class existing.

#include <chrono>

#include <pybind11/pybind11.h>
#include <pybind11_extensions/py_module.hpp>

#include "mutex.hpp"
#include "task_manager/cancel_manager.hpp"

namespace py = pybind11;

namespace Amulet {

class LockNotAcquired : public TaskCancelled {
    using TaskCancelled::TaskCancelled;
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
    void exit(py::object, py::object, py::object);
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
    void exit(py::object, py::object, py::object);
};

class OrderedSharedLock {
    OrderedSharedTimedMutex& mutex;

public:
    OrderedSharedLock(OrderedSharedTimedMutex& mutex);
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
void UniqueLockContextManager::exit(py::object, py::object, py::object)
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
void SharedLockContextManager::exit(py::object, py::object, py::object)
{
    lock.release_shared();
}

OrderedSharedLock::OrderedSharedLock(OrderedSharedTimedMutex& mutex)
    : mutex(mutex)
{
}
bool OrderedSharedLock::acquire_unique(
    bool blocking,
    double timeout,
    AbstractCancelManager& cancel_manager)
{
    if (blocking) {
        if (timeout > 0) {
            return mutex.try_lock_for(std::chrono::duration<double>(timeout), cancel_manager);
        } else {
            return mutex.try_lock_for(std::chrono::duration<double>::max(), cancel_manager);
        }
    } else {
        return mutex.try_lock();
    }
}
void OrderedSharedLock::release_unique()
{
    mutex.unlock();
}
bool OrderedSharedLock::acquire_shared(
    bool blocking,
    double timeout,
    AbstractCancelManager& cancel_manager)
{
    if (blocking) {
        if (timeout > 0) {
            return mutex.try_lock_shared_for(std::chrono::duration<double>(timeout), cancel_manager);
        } else {
            return mutex.try_lock_shared_for(std::chrono::duration<double>::max(), cancel_manager);
        }
    } else {
        return mutex.try_lock_shared();
    }
}
void OrderedSharedLock::release_shared()
{
    mutex.unlock_shared();
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

    auto TaskCancelled = py::module::import("amulet.utils.task_manager").attr("TaskCancelled");
    auto LockNotAcquired = py::register_exception<Amulet::LockNotAcquired>(m, "LockNotAcquired", TaskCancelled);
    LockNotAcquired.doc() = "An exception raised if the lock was not acquired.";

    py::class_<Amulet::UniqueLockContextManager> UniqueLockContextManager(m, "UniqueLockContextManager");
    UniqueLockContextManager.def("__enter__", &Amulet::UniqueLockContextManager::enter);
    UniqueLockContextManager.def("__exit__", &Amulet::UniqueLockContextManager::exit);
    py::class_<Amulet::SharedLockContextManager> SharedLockContextManager(m, "SharedLockContextManager");
    SharedLockContextManager.def("__enter__", &Amulet::SharedLockContextManager::enter);
    SharedLockContextManager.def("__exit__", &Amulet::SharedLockContextManager::exit);

    py::class_<Amulet::OrderedSharedLock> OrderedSharedLock(m, "OrderedSharedLock");
    OrderedSharedLock.def(
        py::init<Amulet::OrderedSharedTimedMutex&>(),
        py::keep_alive<1, 2>());
    OrderedSharedLock.def(
        "acquire_unique",
        &Amulet::OrderedSharedLock::acquire_unique,
        py::arg("blocking") = true,
        py::arg("timeout") = -1.0,
        py::arg("cancel_manager") = Amulet::VoidCancelManager(),
        py::call_guard<py::gil_scoped_release>());
    OrderedSharedLock.def(
        "release_unique",
        &Amulet::OrderedSharedLock::release_unique,
        py::call_guard<py::gil_scoped_release>());
    OrderedSharedLock.def(
        "acquire_shared",
        &Amulet::OrderedSharedLock::acquire_shared,
        py::arg("blocking") = true,
        py::arg("timeout") = -1.0,
        py::arg("cancel_manager") = Amulet::VoidCancelManager(),
        py::call_guard<py::gil_scoped_release>());
    OrderedSharedLock.def(
        "release_shared",
        &Amulet::OrderedSharedLock::release_shared,
        py::call_guard<py::gil_scoped_release>());
    OrderedSharedLock.def(
        "unique",
        &Amulet::OrderedSharedLock::unique,
        py::arg("blocking") = true,
        py::arg("timeout") = -1.0,
        py::arg("cancel_manager") = Amulet::VoidCancelManager(),
        py::call_guard<py::gil_scoped_release>(),
        py::keep_alive<0, 1>());
    OrderedSharedLock.def(
        "shared",
        &Amulet::OrderedSharedLock::shared,
        py::arg("blocking") = true,
        py::arg("timeout") = -1.0,
        py::arg("cancel_manager") = Amulet::VoidCancelManager(),
        py::call_guard<py::gil_scoped_release>(),
        py::keep_alive<0, 1>());
}
