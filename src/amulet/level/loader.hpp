#pragma once

#include <filesystem>
#include <functional>
#include <memory>
#include <stdexcept>
#include <string>

#include <amulet/dll.hpp>
#include <amulet/level/abc/level.hpp>

namespace Amulet {

class LevelLoader {
public:
    class Token {
    public:
        virtual ~Token() = default;
        virtual std::string repr() const = 0;
        virtual size_t hash() const = 0;
        virtual bool operator==(const Token&) const = 0;
    };

    class PathToken : public Token {
    public:
        std::filesystem::path path;
        AMULET_CORE_DLLX PathToken(std::filesystem::path path);
        std::string repr() const override;
        size_t hash() const override;
        bool operator==(const Token&) const override;
    };

    // The name of the loader.
    std::string name;
    // The function to load the level.
    std::function<std::unique_ptr<Level>(const Token&)> loader;

    AMULET_CORE_DLLX LevelLoader(
        const std::string& name,
        std::function<std::unique_ptr<Level>(const Token&)> loader);
};

}

template <>
struct std::hash<Amulet::LevelLoader::Token> {
    size_t operator()(const Amulet::LevelLoader::Token& token) const noexcept;
};

namespace Amulet{

class LevelLoaderRegister {
private:
    std::shared_ptr<LevelLoader> loader;

public:
    AMULET_CORE_DLLX LevelLoaderRegister(const std::shared_ptr<LevelLoader>&);
    AMULET_CORE_DLLX ~LevelLoaderRegister();
};

class NoValidLevelLoader : public std::runtime_error {
    using std::runtime_error::runtime_error;
};

AMULET_CORE_DLLX std::shared_ptr<Level> get_level(const std::shared_ptr<LevelLoader::Token>&);

} // namespace Amulet
