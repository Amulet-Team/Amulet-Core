#include <chrono>

#include "level.hpp"

namespace Amulet {

JavaLevel::JavaLevel(std::unique_ptr<JavaRawLevel> raw_level)
    : _raw_level(std::move(raw_level))
{
}

JavaLevel::~JavaLevel()
{
    close();
}

std::unique_ptr<JavaLevel> JavaLevel::load(const std::filesystem::path& path)
{
    return std::unique_ptr<JavaLevel>(new JavaLevel(JavaRawLevel::load(path)));
}

std::unique_ptr<JavaLevel> JavaLevel::create(const JavaCreateArgsV1& args)
{
    return std::unique_ptr<JavaLevel>(new JavaLevel(JavaRawLevel::create(args)));
}

bool JavaLevel::is_open()
{
    return bool(_open_data);
}

const std::string JavaLevel::get_platform()
{
    return _raw_level->get_platform();
}

const VersionNumber JavaLevel::get_max_game_version()
{
    return _raw_level->get_data_version();
}

bool JavaLevel::is_supported()
{
    return _raw_level->is_supported();
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

const std::filesystem::path& JavaLevel::get_path()
{
    return _raw_level->get_path();
}

void JavaLevel::open()
{
    if (_open_data) {
        return;
    }
    _raw_level->open();
    _open_data = std::make_unique<JavaLevelOpenData>();
    // self._open_data.history_manager.history_changed.connect(self.history_changed)
    opened.emit_async();
}

// void JavaLevel::purge()
//{
//     throw std::runtime_error("NotImplementedError");
// }

void JavaLevel::save()
{
    throw std::runtime_error("NotImplementedError");
}

void JavaLevel::close()
{
    if (!_open_data) {
        return;
    }
    _open_data = nullptr;
    _raw_level->close();
    closed.emit_async();
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
    _raw_level->compact();
}

void JavaLevel::reload_metadata()
{
    _raw_level->reload_metadata();
}

void JavaLevel::reload()
{
    _raw_level->reload();
    reloaded.emit_async();
}

JavaRawLevel& JavaLevel::get_raw_level()
{
    return *_raw_level;
}

} // namespace Amulet
