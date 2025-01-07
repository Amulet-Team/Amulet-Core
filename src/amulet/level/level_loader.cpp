#include <set>
#include <shared_mutex>

#include "level_loader.hpp"

namespace Amulet {

static std::shared_mutex mutex;
static std::set<std::shared_ptr<LevelLoader>> loaders;

LevelLoaderRegister::LevelLoaderRegister(const std::shared_ptr<LevelLoader>& loader)
    : loader(loader)
{
    std::unique_lock lock(mutex);
    loaders.emplace(loader);
}
LevelLoaderRegister::~LevelLoaderRegister()
{
    std::unique_lock lock(mutex);
    loaders.erase(loader);
}

std::unique_ptr<Level> load_level(const LevelLoader::Token& token)
{
    std::shared_lock lock(mutex);
    for (const auto& loader : loaders) {
        try {
            return loader->loader(token);
        } catch (...) {
            continue;
        }
    }
}

} // namespace Amulet
