#include <memory>
#include <mutex>
#include <set>
#include <shared_mutex>

#include "loader.hpp"

size_t std::hash<Amulet::LevelLoader::Token>::operator()(const Amulet::LevelLoader::Token& token) const noexcept
{
    return token.hash();
}

namespace Amulet {

AMULET_CORE_DLLX LevelLoader::PathToken::PathToken(
    std::filesystem::path path)
    : path(path)
{
}
std::string LevelLoader::PathToken::repr() const
{
    return "PathToken(" + path.string() + ")";
}
size_t LevelLoader::PathToken::hash() const
{
    return std::hash(path);
}
bool LevelLoader::PathToken::operator==(const Token& token) const
{
    if (const PathToken* path_token = dynamic_cast<const PathToken*>(&token)) {
        return path == path_token->path;
    }
    return false;
}

AMULET_CORE_DLLX LevelLoader::LevelLoader(
    const std::string& name,
    std::function<std::unique_ptr<Level>(const Token&)> loader)
    : name(name)
    , loader(loader)
{
}

// Level loader storage
static std::set<std::shared_ptr<LevelLoader>> loaders;
static std::shared_mutex loaders_mutex;

AMULET_CORE_DLLX LevelLoaderRegister::LevelLoaderRegister(const std::shared_ptr<LevelLoader>& loader)
    : loader(loader)
{
    std::unique_lock lock(loaders_mutex);
    loaders.emplace(loader);
}
AMULET_CORE_DLLX LevelLoaderRegister::~LevelLoaderRegister()
{
    std::unique_lock lock(loaders_mutex);
    loaders.erase(loader);
}

// Hash based on pointed value
template <typename Ptr>
struct SmartPointerHash {
    std::size_t operator()(const Ptr& ptr) const
    {
        return std::hash<typename Ptr::element_type>()(*ptr);
    }
};

// Equality on pointed value
template <typename Ptr>
struct SmartPointerEqual {
    bool operator()(const Ptr& lhs, const Ptr& rhs) const
    {
        return *lhs == *rhs;
    }
};

// Level storage with mutex
static class LevelData {
public:
    std::mutex mutex;
    std::weak_ptr<Level> level;
};
// Weak map of levels
static std::unordered_map<
    std::shared_ptr<LevelLoader::Token>,
    LevelData,
    SmartPointerHash<std::shared_ptr<LevelLoader::Token>>,
    SmartPointerEqual<std::shared_ptr<LevelLoader::Token>>>
    levels;
// Mutex to modify levels
static std::mutex levels_mutex;

static LevelData& get_level_data(const std::shared_ptr<LevelLoader::Token>& token)
{
    std::unique_lock levels_lock(levels_mutex);
    return levels[token];
}

AMULET_CORE_DLLX std::shared_ptr<Level> get_level(const std::shared_ptr<LevelLoader::Token>& token)
{
    // Get the level storage
    auto& level_data = get_level_data(token);
    // Lock the level storage to stop concurrent calls for this level.
    std::lock_guard<std::mutex> guard(level_data.mutex);
    // If the level already exists return it.
    std::shared_ptr<Level> level = level_data.level.lock();
    if (level) {
        return level;
    }
    // If it doesn't exist then load it.
    std::shared_lock lock(loaders_mutex);
    for (const auto& loader : loaders) {
        try {
            level = loader->loader(*token);
            level_data.level = level;
            return level;
        } catch (...) {
            continue;
        }
    }
    throw NoValidLevelLoader("No loader was able to open token " + token->repr());
}

} // namespace Amulet
