#include <leveldb/cache.h>
#include <leveldb/db.h>
#include <leveldb/decompress_allocator.h>
#include <leveldb/env.h>
#include <leveldb/filter_policy.h>
#include <leveldb/write_batch.h>
#include <leveldb/zlib_compressor.h>

#include "history.hpp"

class NullLogger : public leveldb::Logger {
public:
    void Logv(const char*, va_list) override { }
};

class LevelDBOptions : public Amulet::LevelDBOptions {
public:
    NullLogger logger;
    leveldb::ZlibCompressorRaw zlib_compressor_raw;
    leveldb::ZlibCompressor zlib_compressor;
    leveldb::DecompressAllocator decompress_allocator;
};

static std::unique_ptr<Amulet::LevelDB> create_leveldb(const std::string& path_str)
{
    // Expand dots and symbolic links
    auto path = std::filesystem::absolute(path_str);
    // If there is not a directory at the path
    if (!std::filesystem::is_directory(path)) {
        throw std::runtime_error("leveldb directory does not exist.");
    }

    // Make a db directory in the directory
    path /= "db";
    std::filesystem::create_directory(path);

    auto options = std::make_unique<LevelDBOptions>();
    options->options.create_if_missing = true;
    options->options.filter_policy = leveldb::NewBloomFilterPolicy(10);
    options->options.block_cache = leveldb::NewLRUCache(40 * 1024 * 1024);
    options->options.write_buffer_size = 4 * 1024 * 1024;
    options->options.info_log = &options->logger;
    options->options.compressors[0] = &options->zlib_compressor_raw;
    options->options.compressors[1] = &options->zlib_compressor;
    options->options.block_size = 163840;

    options->read_options.decompress_allocator = &options->decompress_allocator;

    leveldb::DB* _db = NULL;
    auto status = leveldb::DB::Open(options->options, path.string(), &_db);
    if (status.code() == leveldb::Status::kOk) {
        return std::make_unique<Amulet::LevelDB>(
            std::unique_ptr<leveldb::DB>(_db),
            std::move(options));
    }
    throw std::runtime_error("Could not create temporary leveldb database at \"" + path_str + "\" " + status.ToString());
}

namespace Amulet {

// HistoryManagerPrivate

namespace detail {

    HistoryManagerPrivate::HistoryManagerPrivate()
        : db_path("level_data")
        , db(create_leveldb(db_path.get_path().string()))
    {
        // Add an initial bin.
        history_bins.emplace_back();
    }

    void HistoryManagerPrivate::invalidate_future()
    {
        // If there are future bins to invalidate.
        if (has_redo()) {
            // Destroy future bins
            history_bins.resize(history_index + 1);
            // Call invalidate_future for each layer
            for_each<AbstractHistoryManagerLayer>(
                layers,
                [](AbstractHistoryManagerLayer& layer) { layer.invalidate_future(); });
        }
    }

    bool HistoryManagerPrivate::has_redo()
    {
        return history_index + 1 < history_bins.size();
    }

} // namespace detail

// HistoryManager

HistoryManager::HistoryManager()
    : _h(std::make_shared<detail::HistoryManagerPrivate>())
{
}

std::shared_mutex& HistoryManager::get_mutex()
{
    return _h->mutex;
}

void HistoryManager::reset()
{
    // Reset each layer
    for_each<AbstractHistoryManagerLayer>(
        _h->layers,
        [](AbstractHistoryManagerLayer& layer) { layer.reset(); });
    // Clear all history bins
    _h->history_bins.clear();
    // Add the initial bin.
    _h->history_bins.emplace_back();
    // Update the index to the initial bin.
    _h->history_index = 0;
}

void HistoryManager::mark_saved()
{
    for_each<AbstractHistoryManagerLayer>(
        _h->layers,
        [](AbstractHistoryManagerLayer& layer) { layer.mark_saved(); });
}

void HistoryManager::create_undo_bin()
{
    // Invalidate all future undo bins
    _h->invalidate_future();
    // Add a new bin
    _h->history_bins.emplace_back();
    _h->history_index++;
}

size_t HistoryManager::get_undo_count()
{
    return _h->history_index;
}

void HistoryManager::undo()
{
    // Check if there is anything to undo.
    if (_h->history_index == 0) {
        throw std::runtime_error("There is nothing to undo.");
    }
    // Decrement the history index.
    auto old_index = _h->history_index;
    auto new_index = --_h->history_index;
    // For all resources in the bin.
    for_each<HistoryResource>(
        _h->history_bins.at(old_index),
        [&new_index](HistoryResource& resource) {
            // Decrement the indexes.
            resource.index--;
            resource.global_index = new_index;
            // Notify listeners that it has changed.
            resource.changed->emit();
        });
}

size_t HistoryManager::get_redo_count()
{
    return _h->history_bins.size() - _h->history_index - 1;
}

void HistoryManager::redo()
{
    // Check if there is anything to redo.
    if (!_h->has_redo()) {
        throw std::runtime_error("There is nothing to redo.");
    }
    // Increment the history index.
    auto new_index = ++_h->history_index;
    // For all resources in the bin.
    for_each<HistoryResource>(
        _h->history_bins.at(new_index),
        [&new_index](HistoryResource& resource) {
            // Increment the index
            resource.index++;
            resource.global_index = new_index;
            // Notify listeners that it has changed.
            resource.changed->emit();
        });
}

} // namespace Amulet
