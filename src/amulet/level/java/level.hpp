#pragma once

#include <filesystem>

#include <amulet/level/abc/level.hpp>
#include "raw_level.hpp"

namespace Amulet {

class JavaLevel : public Level {
public:
    // Load an existing Java level from the given directory.
    // Thread safe.
    AMULET_CORE_EXPORT static std::unique_ptr<JavaLevel> load(const std::filesystem::path&);

    // Create a new Java level at the given directory.
    // Thread safe.
    AMULET_CORE_EXPORT static std::unique_ptr<JavaLevel> create(const JavaCreateArgsV1&);
};

} // namespace Amulet
