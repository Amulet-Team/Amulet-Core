#pragma once

#include <filesystem>
#include <memory>
#include <string>

#include "lock_file.hpp"

namespace Amulet {

// Get the directory in which temporary directories will be created.
// This is configurable by setting the "CACHE_DIR" environment variable.
// Thread safe.
std::filesystem::path get_temp_dir();

// A temporary directory to do with as you wish.
class TempDir {
private:
    std::filesystem::path _path;
    std::unique_ptr<Amulet::LockFile> _lock;

public:
    // Construct a new temporary directory.
    // Thread safe.
    TempDir(const std::string& group);

    // TempDir destructor.
    // This automatically deletes the temporary directory.
    ~TempDir();

    // Get the path of the temporary directory.
    // Thread safe.
    const std::filesystem::path& get_path() const;
};

} // namespace Amulet
