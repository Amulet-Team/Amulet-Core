#include <chrono>
#include <mutex>
#include <shared_mutex>

#include "level.hpp"

namespace Amulet {

JavaLevelOpenData::JavaLevelOpenData()
    : history_enabled(std::make_shared<bool>(true))
{
}

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
    auto& mutex = _raw_level->get_mutex();
    mutex.lock<Amulet::ThreadAccessMode::Read, Amulet::ThreadShareMode::SharedReadWrite>();
    std::lock_guard lock(mutex, std::adopt_lock);
    return _raw_level->get_data_version();
}

bool JavaLevel::is_supported()
{
    return _raw_level->is_supported();
}

PIL::Image::Image JavaLevel::get_thumbnail()
{
    return _raw_level->get_thumbnail();
};

const std::string JavaLevel::get_level_name()
{
    auto& mutex = _raw_level->get_mutex();
    mutex.lock<Amulet::ThreadAccessMode::Read, Amulet::ThreadShareMode::SharedReadWrite>();
    std::lock_guard lock(mutex, std::adopt_lock);
    return _raw_level->get_level_name();
}

std::chrono::system_clock::time_point JavaLevel::get_modified_time()
{
    auto& mutex = _raw_level->get_mutex();
    mutex.lock<Amulet::ThreadAccessMode::Read, Amulet::ThreadShareMode::SharedReadWrite>();
    std::lock_guard lock(mutex, std::adopt_lock);
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
    {
        auto& mutex = _raw_level->get_mutex();
        mutex.lock<Amulet::ThreadAccessMode::ReadWrite, Amulet::ThreadShareMode::Unique>();
        std::lock_guard lock(mutex, std::adopt_lock);
        _raw_level->open();
    }
    _open_data = std::make_unique<JavaLevelOpenData>();
    opened.emit();
}

void JavaLevel::purge()
{
    {
        auto& open_data = _get_open_data();
        std::lock_guard lock(open_data.history_manager.get_mutex());
        open_data.history_manager.reset();
    }
    purged.emit();
    history_changed.emit();
}

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
    {
        auto& mutex = _raw_level->get_mutex();
        mutex.lock<Amulet::ThreadAccessMode::ReadWrite, Amulet::ThreadShareMode::Unique>();
        std::lock_guard lock(mutex, std::adopt_lock);
        _raw_level->close();
    }
    closed.emit();
}

void JavaLevel::create_restore_point()
{
    {
        auto& open_data = _get_open_data();
        std::lock_guard lock(open_data.history_manager.get_mutex());
        open_data.history_manager.create_undo_bin();
    }
    history_changed.emit();
}

size_t JavaLevel::get_undo_count()
{
    auto& open_data = _get_open_data();
    std::shared_lock lock(open_data.history_manager.get_mutex());
    return open_data.history_manager.get_undo_count();
}

void JavaLevel::undo()
{
    {
        auto& open_data = _get_open_data();
        std::lock_guard lock(open_data.history_manager.get_mutex());
        open_data.history_manager.undo();
    }
    history_changed.emit();
}

size_t JavaLevel::get_redo_count()
{
    auto& open_data = _get_open_data();
    std::shared_lock lock(open_data.history_manager.get_mutex());
    return open_data.history_manager.get_redo_count();
}

void JavaLevel::redo()
{
    {
        auto& open_data = _get_open_data();
        std::lock_guard lock(open_data.history_manager.get_mutex());
        open_data.history_manager.redo();
    }
    history_changed.emit();
}

bool JavaLevel::get_history_enabled()
{
    return *_get_open_data().history_enabled;
}

void JavaLevel::set_history_enabled(bool history_enabled)
{
    *_get_open_data().history_enabled = history_enabled;
    history_enabled_changed.emit();
}

std::vector<std::string> JavaLevel::get_dimension_ids()
{
    auto& mutex = _raw_level->get_mutex();
    mutex.lock<Amulet::ThreadAccessMode::Read, Amulet::ThreadShareMode::SharedReadWrite>();
    std::lock_guard lock(mutex, std::adopt_lock);
    return _raw_level->get_dimension_ids();
}

std::shared_ptr<JavaDimension> JavaLevel::get_java_dimension(const DimensionID& dimension_id)
{
    auto& open_data = _get_open_data();
    {
        // Find the dimension with a shared lock.
        std::shared_lock dimensions_lock(open_data.dimensions_mutex);
        auto it = open_data.dimensions.find(dimension_id);
        if (it != open_data.dimensions.end()) {
            return it->second;
        }
    }
    {
        // If it doesn't exist try again with a unique lock.
        std::lock_guard dimensions_lock(open_data.dimensions_mutex);
        auto it = open_data.dimensions.find(dimension_id);
        if (it != open_data.dimensions.end()) {
            return it->second;
        }
        OrderedLockGuard<
            ThreadAccessMode::Read,
            ThreadShareMode::SharedReadWrite>
            raw_level_lock(_raw_level->get_mutex());
        auto raw_dimension = _raw_level->get_dimension(dimension_id);
        auto dimension = std::shared_ptr<JavaDimension>(new JavaDimension(
            raw_dimension,
            open_data.history_manager,
            open_data.history_enabled));
        open_data.dimensions.emplace(raw_dimension->get_dimension_id(), dimension);
        open_data.dimensions.emplace(raw_dimension->get_relative_path(), dimension);
        return dimension;
    }
}

std::shared_ptr<Dimension> JavaLevel::get_dimension(const DimensionID& dimension_id)
{
    return get_java_dimension(dimension_id);
}

void JavaLevel::compact()
{
    auto& mutex = _raw_level->get_mutex();
    mutex.lock<Amulet::ThreadAccessMode::Read, Amulet::ThreadShareMode::SharedReadWrite>();
    std::lock_guard lock(mutex, std::adopt_lock);
    _raw_level->compact();
}

void JavaLevel::reload_metadata()
{
    std::lock_guard lock(_raw_level->get_mutex());
    _raw_level->reload_metadata();
}

void JavaLevel::reload()
{
    {
        // purge loaded data.
        auto& open_data = _get_open_data();
        std::lock_guard lock(open_data.history_manager.get_mutex());
        open_data.history_manager.reset();
    }
    {
        // reload the raw level.
        std::lock_guard lock(_raw_level->get_mutex());
        _raw_level->reload();
    }
    reloaded.emit();
    history_changed.emit();
}

JavaRawLevel& JavaLevel::get_raw_level()
{
    return *_raw_level;
}

} // namespace Amulet
