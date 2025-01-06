#pragma once
#include <filesystem>

namespace Amulet {

class CompactibleLevel {
public:
    virtual ~CompactibleLevel() {};

    // Compact the level data to reduce file size.
    virtual void compact() = 0;
};

class DiskLevel {
public:
    virtual ~DiskLevel() {};

    // The path to the level on disk.
    virtual std::filesystem::path path() = 0;
};

class ReloadableLevel {
public:
    virtual ~ReloadableLevel() {};

    // Reload the metadata in the existing instance.
    // This can only be done when the level is not open.
    virtual void reload() = 0;
};

} // namespace Amulet
