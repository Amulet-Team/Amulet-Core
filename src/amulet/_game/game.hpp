#pragma once

#include <string>
#include <memory>

#include <amulet/version/version.hpp>
#include "abc/version.hpp"
#include "java/version.hpp"

namespace Amulet {

std::shared_ptr<GameVersion> get_game_version(const std::string&, const VersionNumber& version);
std::shared_ptr<JavaGameVersion> get_java_game_version(const VersionNumber& version);

} // namespace Amulet
