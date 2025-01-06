#pragma once

#include <filesystem>
#include <string>
#include <memory>

#include "level.hpp"

namespace Amulet {

class LevelLoader {
public:
    class Token {
    public:
        virtual ~Token() { }
    };

    class PathToken : public Token {
    public:
        std::filesystem::path path;
        PathToken(std::filesystem::path path)
            : path(path)
        {
        }
    };

    virtual ~LevelLoader() {};

    // The name of the loader.
    virtual std::string name() const = 0;

    // Can the loader load the level token.
    virtual bool can_load(const Token&) const = 0;

    // Load the level from the token.
    virtual std::unique_ptr<Level> load(const Token&) const = 0;
};

} // namespace Amulet
