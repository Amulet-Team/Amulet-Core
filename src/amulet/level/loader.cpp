#include <set>
#include <shared_mutex>

#include "loader.hpp"

namespace Amulet {

AMULET_CORE_DLLX LevelLoader::PathToken::PathToken(std::filesystem::path path)
    : path(path)
{
}
std::string LevelLoader::PathToken::repr() const
{
    return "PathToken(" + path.string() + ")";
}

AMULET_CORE_DLLX LevelLoader::LevelLoader(
    const std::string& name,
    std::function<std::unique_ptr<Level>(const Token&)> loader)
    : name(name)
    , loader(loader)
{
}

static std::shared_mutex mutex;
static std::set<std::shared_ptr<LevelLoader>> loaders;

AMULET_CORE_DLLX LevelLoaderRegister::LevelLoaderRegister(const std::shared_ptr<LevelLoader>& loader)
    : loader(loader)
{
    std::unique_lock lock(mutex);
    loaders.emplace(loader);
}
AMULET_CORE_DLLX LevelLoaderRegister::~LevelLoaderRegister()
{
    std::unique_lock lock(mutex);
    loaders.erase(loader);
}

AMULET_CORE_DLLX std::unique_ptr<Level> load_level(const LevelLoader::Token& token)
{
    std::shared_lock lock(mutex);
    for (const auto& loader : loaders) {
        try {
            return loader->loader(token);
        } catch (...) {
            continue;
        }
    }
    throw NoValidLevelLoader("No loader was able to open token " + token.repr());
}

} // namespace Amulet
