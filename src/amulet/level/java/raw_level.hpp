#pragma once

#include <chrono>
#include <filesystem>
#include <memory>

#include <amulet_nbt/tag/named_tag.hpp>

#include <amulet/dll.hpp>
#include <amulet/utils/mutex.hpp>
#include <amulet/version.hpp>
#include <amulet/level/abc/registry.hpp>

#include "dimension.hpp"
#include "raw_dimension.hpp"

namespace Amulet {

struct JavaCreateArgsV1 {
    bool overwrite;
    std::filesystem::path path;
    VersionNumber version;
    std::string level_name;
};

class JavaRawLevel {
private:
    Amulet::OrderedSharedTimedMutex mutex;

public:
    AMULET_CORE_EXPORT static std::unique_ptr<JavaRawLevel> load(const std::filesystem::path&);
    AMULET_CORE_EXPORT static std::unique_ptr<JavaRawLevel> create(const JavaCreateArgsV1&);

    AMULET_CORE_EXPORT bool is_open() const;
    AMULET_CORE_EXPORT void reload();
    AMULET_CORE_EXPORT void open();
    AMULET_CORE_EXPORT void close();
    AMULET_CORE_EXPORT const std::filesystem::path path() const;
    AMULET_CORE_EXPORT AmuletNBT::NamedTag get_level_dat() const;
    AMULET_CORE_EXPORT void set_level_dat(const AmuletNBT::NamedTag&);
    AMULET_CORE_EXPORT std::string platform();
    AMULET_CORE_EXPORT const VersionNumber& data_version();
    AMULET_CORE_EXPORT std::chrono::system_clock::time_point modified_time();
    AMULET_CORE_EXPORT std::string level_name();
    AMULET_CORE_EXPORT void set_level_name(const std::string&);
    AMULET_CORE_EXPORT std::vector<std::string> dimension_ids();
    AMULET_CORE_EXPORT std::shared_ptr<JavaRawDimension> get_dimension();
    AMULET_CORE_EXPORT void compact();
    AMULET_CORE_EXPORT std::shared_ptr<IdRegistry> get_block_id_override();
    AMULET_CORE_EXPORT std::shared_ptr<IdRegistry> get_biome_id_override();

};

} // namespace Amulet
