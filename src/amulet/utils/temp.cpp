#include "temp.hpp"

#include <chrono>
#include <cstdlib>
#include <filesystem>

#include "lock_file.hpp"

namespace Amulet {

std::filesystem::path get_temp_dir()
{
    auto* path_ptr = std::getenv("CACHE_DIR");
    if (path_ptr == nullptr) {
        throw std::runtime_error("Environment variable CACHE_DIR does not exist.");
    }
    std::filesystem::path path(path_ptr);
    if (!std::filesystem::is_directory(path)) {
        throw std::runtime_error("Environment variable CACHE_DIR is not a directory.");
    }
    return path;
}

TempDir::TempDir(const std::string& group)
{
    auto time = std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::system_clock::now().time_since_epoch())
                    .count();
    for (size_t i = 0; i < 100; i++) {
        auto path = get_temp_dir() / group / ("amulettmp-" + std::to_string(time) + "-" + std::to_string(i));
        std::filesystem::create_directories(path);
        try {
            _lock = std::make_unique<Amulet::LockFile>(path / "lock");
        } catch (const std::runtime_error&) {
            continue;
        }
        _path = path;
        return;
    }
    throw std::runtime_error("Could not create temporary directory.");
}

TempDir::~TempDir() {
    _lock.reset();
    std::filesystem::remove_all(_path);
}

const std::filesystem::path& TempDir::get_path() const {
    return _path;
}

} // namespace Amulet

static const bool cleared_temp_dirs = [] {
    std::filesystem::path temp_dir;
    try {
        temp_dir = Amulet::get_temp_dir();
    } catch (const std::runtime_error&) {
        return true;
    }
    
    for (const auto& group : std::filesystem::directory_iterator(temp_dir)) {
        if (!group.is_directory()) {
            continue;
        }
        for (const auto& dir : std::filesystem::directory_iterator(group.path())) {
            if (!dir.path().filename().string().starts_with("amulettmp-")) {
                continue;
            }
            try {
                Amulet::LockFile lock(dir.path() / "lock");
            } catch (const std::runtime_error&) {
                continue;
            }
            std::filesystem::remove_all(dir.path());
        }
    }
    return true;
}();
