#include <pybind11/pybind11.h>

#include <optional>
#include <string>

#include <amulet/utils/lock_file.hpp>

namespace py = pybind11;

static std::optional<Amulet::LockFile> test_lock_file;

void init_test_lock_file(py::module m_parent)
{
    auto m = m_parent.def_submodule("test_lock_file_");
    m.def(
        "test_lock_file",
        [](const std::string& path) {
            Amulet::LockFile lock_file(path);
            Amulet::LockFile lock_file_2(std::move(lock_file));
            Amulet::LockFile lock_file_3 = std::move(lock_file_2);
            lock_file_3.unlock_file();
        });

    m.def(
        "create_test_file",
        [](const std::string& path) {
            test_lock_file = Amulet::LockFile(path);
            test_lock_file->write_to_file("Hello World");
        });

    m.def(
        "unlock_test_file",
        []() {
            if (!test_lock_file) {
                throw std::runtime_error("Lock file has not been initialised.");
            }
            test_lock_file->unlock_file();
        });
}
