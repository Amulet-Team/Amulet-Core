#include <chrono>

#include "level.hpp"

namespace Amulet {

JavaLevel::JavaLevel(std::unique_ptr<JavaRawLevel> raw_level)
    : _raw_level(std::move(raw_level))
{
}

std::unique_ptr<JavaLevel> JavaLevel::load(const std::filesystem::path& path)
{
    return std::make_unique<JavaLevel>(JavaRawLevel::load(path));
}

std::unique_ptr<JavaLevel> JavaLevel::create(const JavaCreateArgsV1& args)
{
    return std::make_unique<JavaLevel>(JavaRawLevel::create(args));
}

bool JavaLevel::is_open()
{
    return _raw_level->is_open();
}

const std::string JavaLevel::get_platform()
{
    return _raw_level->get_platform();
}

const VersionNumber JavaLevel::get_max_game_version()
{
    return _raw_level->get_data_version();
}

const std::string JavaLevel::get_level_name()
{
    return _raw_level->get_level_name();
}

std::chrono::system_clock::time_point JavaLevel::get_modified_time()
{
    return _raw_level->get_modified_time();
}

size_t JavaLevel::get_sub_chunk_size()
{
    return 16;
}

void JavaLevel::open()
{
    _raw_level->open();
}

void JavaLevel::purge()
{
    throw std::runtime_error("NotImplementedError");
}

void JavaLevel::save()
{
    throw std::runtime_error("NotImplementedError");
}

void JavaLevel::close()
{
    _raw_level->close();
}

// size_t JavaLevel::undo_count();
// void JavaLevel::undo();
// size_t JavaLevel::redo_count();
// void JavaLevel::redo();
// bool JavaLevel::is_history_enabled();
// void JavaLevel::set_history_enabled(bool);

std::vector<std::string> JavaLevel::get_dimension_ids()
{
    return _raw_level->get_dimension_ids();
}

std::shared_ptr<Dimension> JavaLevel::get_dimension(const std::string&)
{
    throw std::runtime_error("NotImplementedError");
}

void JavaLevel::compact()
{
    throw std::runtime_error("NotImplementedError");
}

const std::filesystem::path& JavaLevel::get_path()
{
    return _raw_level->get_path();
}

void JavaLevel::reload_metadata()
{
    throw std::runtime_error("NotImplementedError");
}

} // namespace Amulet
