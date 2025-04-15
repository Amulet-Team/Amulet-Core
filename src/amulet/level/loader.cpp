#include <memory>
#include <mutex>
#include <set>
#include <shared_mutex>

#include "loader.hpp"

size_t std::hash<Amulet::LevelLoaderToken>::operator()(const Amulet::LevelLoaderToken& token) const noexcept
{
    return token.hash();
}

namespace Amulet {

LevelLoaderPathToken::LevelLoaderPathToken(
    std::filesystem::path path)
    : path(path)
{
}
std::string LevelLoaderPathToken::repr() const
{
    return "LevelLoaderPathToken(" + path.string() + ")";
}
size_t LevelLoaderPathToken::hash() const
{
    return std::hash<std::filesystem::path> {}(path);
}
bool LevelLoaderPathToken::operator==(const LevelLoaderToken& token) const
{
    if (const LevelLoaderPathToken* path_token = dynamic_cast<const LevelLoaderPathToken*>(&token)) {
        return path == path_token->path;
    }
    return false;
}

LevelLoader::LevelLoader(
    const std::string& name,
    std::function<std::unique_ptr<Level>(const LevelLoaderToken&)> loader)
    : name(name)
    , loader(loader)
{
}

// Level loader storage
static std::set<std::shared_ptr<LevelLoader>>& get_loaders()
{
    static std::set<std::shared_ptr<LevelLoader>> loaders;
    return loaders;
}
static std::shared_mutex& get_loaders_mutex()
{
    static std::shared_mutex loaders_mutex;
    return loaders_mutex;
}

LevelLoaderRegister::LevelLoaderRegister(std::shared_ptr<LevelLoader> loader)
    : _loader(std::move(loader))
{
    std::unique_lock lock(get_loaders_mutex());
    get_loaders().emplace(_loader);
}
LevelLoaderRegister::~LevelLoaderRegister()
{
    std::unique_lock lock(get_loaders_mutex());
    get_loaders().erase(_loader);
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
class LevelData {
public:
    std::mutex mutex;
    std::weak_ptr<Level> level;
};
// Weak map of levels
static std::unordered_map<
    std::shared_ptr<LevelLoaderToken>,
    LevelData,
    SmartPointerHash<std::shared_ptr<LevelLoaderToken>>,
    SmartPointerEqual<std::shared_ptr<LevelLoaderToken>>>
    levels;
// Mutex to modify levels
static std::mutex levels_mutex;

static LevelData& get_level_data(const std::shared_ptr<LevelLoaderToken>& token)
{
    std::unique_lock levels_lock(levels_mutex);
    return levels[token];
}

std::shared_ptr<Level> get_level(std::shared_ptr<LevelLoaderToken> token)
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
    std::shared_lock lock(get_loaders_mutex());
    for (const auto& loader : get_loaders()) {
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
