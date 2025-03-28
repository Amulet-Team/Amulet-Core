#include <pybind11/pybind11.h>

#include "game.hpp"

namespace py = pybind11;

namespace Amulet {

std::shared_ptr<GameVersion> get_game_version(const std::string& platform, const VersionNumber& version)
{
    py::gil_scoped_acquire gil;
    return std::make_shared<GameVersion>(py::module::import("amulet.game").attr("get_game_version")(py::cast(platform), py::cast(version)));
}

std::shared_ptr<JavaGameVersion> get_java_game_version(const VersionNumber& version)
{
    py::gil_scoped_acquire gil;
    return std::make_shared<JavaGameVersion>(py::module::import("amulet.game").attr("get_game_version")(py::str("java"), py::cast(version)));
}

} // namespace Amulet
