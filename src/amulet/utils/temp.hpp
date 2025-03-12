#pragma once

#include <filesystem>
#include <memory>
#include <string>

#include "lock_file.hpp"

namespace Amulet {

std::filesystem::path get_temp_dir();

// A temporary directory to do with as you wish.
class TempDir {
private:
    std::filesystem::path _path;
    std::unique_ptr<Amulet::LockFile> _lock;

public:
    TempDir(const std::string& group);
    ~TempDir();
    const std::filesystem::path& get_path() const;
};

} // namespace Amulet
