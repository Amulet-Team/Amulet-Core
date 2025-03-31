#pragma once

#include <amulet/_game/abc/version.hpp>

#include "block.hpp"

namespace Amulet {

class JavaGameVersion : public GameVersion {
public:
    using GameVersion::GameVersion;

    std::shared_ptr<JavaBlockData> get_block_data();
};

} // namespace Amulet
