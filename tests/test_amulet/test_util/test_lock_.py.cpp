#include <pybind11/pybind11.h>

#include <shared_mutex>

#include <pybind11_extensions/py_module.hpp>

#include <amulet/utils/mutex.hpp>

namespace py = pybind11;

void init_test_lock(py::module m_parent){
    auto m = m_parent.def_submodule("test_lock_");
    m.def("throw_deadlock", [](){ throw Amulet::Deadlock("Deadlock encountered."); });

    m.def("lock_ordered_mutex", [](Amulet::OrderedMutex& mutex, size_t count) {
        for (size_t i = 0; i < count; i++) {
            mutex.lock<Amulet::CurrentThreadMode::ReadWrite, Amulet::OtherThreadMode::ReadWrite>();
            mutex.unlock();
        }
    });

    m.def("lock_shared_mutex", [](std::shared_mutex& mutex, size_t count) {
        for (size_t i = 0; i < count; i++) {
            mutex.lock_shared();
            mutex.unlock_shared();
        }
    });
}
