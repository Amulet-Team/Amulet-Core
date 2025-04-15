#pragma once

#include <filesystem>
#include <functional>
#include <memory>
#include <stdexcept>
#include <string>

#include <amulet/dll.hpp>
#include <amulet/level/abc/level.hpp>

namespace Amulet {

class LevelLoaderToken {
public:
    virtual ~LevelLoaderToken() = default;
    virtual std::string repr() const = 0;
    virtual size_t hash() const = 0;
    virtual bool operator==(const LevelLoaderToken&) const = 0;
};

class LevelLoaderPathToken : public LevelLoaderToken {
public:
    std::filesystem::path path;
    AMULET_CORE_EXPORT LevelLoaderPathToken(std::filesystem::path path);
    AMULET_CORE_EXPORT LevelLoaderPathToken(const LevelLoaderPathToken& token) = default;
    std::string repr() const override;
    size_t hash() const override;
    bool operator==(const LevelLoaderToken&) const override;
};

class LevelLoader {
public:
    // The name of the loader.
    std::string name;
    // The function to load the level.
    std::function<std::unique_ptr<Level>(const LevelLoaderToken&)> loader;

    AMULET_CORE_EXPORT LevelLoader(
        const std::string& name,
        std::function<std::unique_ptr<Level>(const LevelLoaderToken&)> loader);
};

}

template <>
struct std::hash<Amulet::LevelLoaderToken> {
    size_t operator()(const Amulet::LevelLoaderToken& token) const noexcept;
};

namespace Amulet {

class LevelLoaderRegister {
private:
    std::shared_ptr<LevelLoader> _loader;

public:
    AMULET_CORE_EXPORT LevelLoaderRegister(std::shared_ptr<LevelLoader>);
    AMULET_CORE_EXPORT ~LevelLoaderRegister();
};

class NoValidLevelLoader : public std::runtime_error {
    using std::runtime_error::runtime_error;
};

AMULET_CORE_EXPORT std::shared_ptr<Level> get_level(std::shared_ptr<LevelLoaderToken>);

} // namespace Amulet
