#pragma once

#include <filesystem>
#include <functional>
#include <memory>
#include <string>

#include <amulet/dll.hpp>
#include <amulet/level/abc/level.hpp>

namespace Amulet {

class LevelLoader {
public:
    class Token {
    public:
        virtual ~Token() = default;
    };

    class PathToken : public Token {
    public:
        std::filesystem::path path;
        PathToken(std::filesystem::path path)
            : path(path)
        {
        }
    };

    // The name of the loader.
    std::string name;
    // The function to load the level.
    std::function<std::unique_ptr<Level>(const Token&)> loader;
    
    LevelLoader(
        const std::string& name,
        std::function<std::unique_ptr<Level>(const Token&)> loader
    )
        : name(name)
        , loader(loader)
    {
    }
};

class LevelLoaderRegister {
private:
    std::shared_ptr<LevelLoader> loader;

public:
    LevelLoaderRegister(const std::shared_ptr<LevelLoader>&);
    ~LevelLoaderRegister();
};

std::unique_ptr<Level> load_level(const LevelLoader::Token&);

} // namespace Amulet
