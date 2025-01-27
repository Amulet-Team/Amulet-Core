#include <stdexcept>
#include <iostream>

#include <pybind11/pybind11.h>
#include <pybind11_extensions/py_module.hpp>

#include <amulet/utils/task_manager/cancel_manager.hpp>

namespace py = pybind11;

void init_test_task_manager(py::module m_parent)
{
    auto m = pybind11_extensions::def_subpackage(m_parent, "test_task_manager_");
    m.def("throw_task_cancelled", [](){ throw Amulet::TaskCancelled(); });
    m.def("cpp_test_task_cancelled", []() {
        std::string hello_world = "Hello World";
        std::string task_cancelled = "Task Cancelled";
        try {
            throw Amulet::TaskCancelled(hello_world);
        } catch (const std::exception& e) {
            if (e.what() != hello_world) {
                throw std::runtime_error("1. what() != 'Hello World'. " + std::string(e.what()));
            }
        }
        try {
            throw Amulet::TaskCancelled();
        } catch (const std::exception& e) {
            if (e.what() != task_cancelled) {
                throw std::runtime_error("2. what() != 'Task Cancelled'." + std::string(e.what()));
            }
        }
        try {
            throw Amulet::TaskCancelled(hello_world);
        } catch (const Amulet::TaskCancelled& e) {
            if (e.what() != hello_world) {
                throw std::runtime_error("3. what() != 'Hello World'." + std::string(e.what()));
            }
        }
        try {
            throw Amulet::TaskCancelled();
        } catch (const Amulet::TaskCancelled& e) {
            if (e.what() != task_cancelled) {
                throw std::runtime_error("4. what() != 'Task Cancelled'." + std::string(e.what()));
            }
        }

        // Test copy
        Amulet::TaskCancelled e1;
        try {
            throw Amulet::TaskCancelled(hello_world);
        } catch (const Amulet::TaskCancelled& e) {
            e1 = e;
            if (e1.what() != hello_world) {
                throw std::runtime_error("5. what() != 'Hello World'. " + std::string(e1.what()));
            }
            Amulet::TaskCancelled e2(e);
            if (e2.what() != hello_world) {
                throw std::runtime_error("6. what() != 'Hello World'. " + std::string(e2.what()));
            }
        }
    });
}
