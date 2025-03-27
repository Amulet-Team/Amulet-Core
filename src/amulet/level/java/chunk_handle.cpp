#include <stdexcept>
#include <variant>

#include <amulet/utils/mutex.hpp>

#include "chunk_handle.hpp"

namespace Amulet {

JavaChunkHandle::JavaChunkHandle(
    const DimensionID& dimension_id,
    std::int64_t cx,
    std::int64_t cz,
    std::shared_ptr<JavaRawDimension> raw_dimension,
    std::shared_ptr<HistoryManagerLayer<detail::ChunkKey>> chunk_history,
    std::shared_ptr<HistoryManagerLayer<std::string>> chunk_data_history)
    : ChunkHandle(dimension_id, cx, cz)
    , _raw_dimension(std::move(raw_dimension))
    , _chunk_history(std::move(chunk_history))
    , _chunk_data_history(std::move(chunk_data_history))
{
}

bool JavaChunkHandle::exists()
{
    {
        std::shared_lock history_lock(_chunk_history->get_mutex());
        if (_chunk_history->has_resource(_key)) {
            return !_chunk_history->get_value(_key).empty();
        }
        OrderedLockGuard<ThreadAccessMode::Read, ThreadShareMode::SharedReadWrite> raw_lock(_raw_dimension->get_mutex());
        return _raw_dimension->has_chunk(_cx, _cz);
    }
}

std::unique_ptr<JavaChunk> JavaChunkHandle::_get_null_chunk()
{
    std::string data = _chunk_history->get_value(_key);
    if (data.empty()) {
        // Empty if chunk does not exist.
        throw ChunkDoesNotExist();
    } else if (data[0]) {
        // 1 followed by the string if other error.
        throw ChunkLoadError(data.substr(1));
    } else {
        // 0 followed by the chunk id if a valid chunk.
        return detail::get_java_null_chunk(data.substr(1));
    }
}

void JavaChunkHandle::_preload() {
    throw std::runtime_error("NotImplementedError");
}

std::unique_ptr<JavaChunk> JavaChunkHandle::get_java_chunk(std::optional<std::set<std::string>> component_ids)
{
    auto get_chunk = [&]() -> std::unique_ptr<JavaChunk> {
        // Load the chunk from the cache.
        auto chunk = _get_null_chunk();
        auto chunk_component_ids = chunk->get_component_ids();
        std::set<std::string> valid_components;
        if (component_ids) {
            // Filter the requested component ids to those in the chunk.
            std::set_intersection(
                chunk_component_ids.begin(), chunk_component_ids.end(),
                component_ids->begin(), component_ids->end(),
                std::inserter(valid_components, valid_components.begin()));
        } else {
            // Get all component ids in the chunk.
            valid_components = std::move(chunk_component_ids);
        }

        // Load all the requested component ids.
        SerialisedComponents component_data;
        for (const auto& component_id : valid_components) {
            component_data.emplace(
                component_id,
                _chunk_data_history->get_value(std::string(_key) + '/' + component_id));
        }

        chunk->reconstruct_chunk(component_data);
        return chunk;
    };

    {
        std::shared_lock lock(_chunk_history->get_mutex());
        if (_chunk_history->has_resource(_key)) {
            // Get the chunk if it has previously been populated.
            return get_chunk();
        }
    }
    {
        std::lock_guard lock(_chunk_history->get_mutex());
        if (!_chunk_history->has_resource(_key)) {
            // Load the chunk if it wasn't previously populated.
            _preload();
        }
    }
    {
        std::shared_lock lock(_chunk_history->get_mutex());
        // Get the chunk.
        return get_chunk();
    }
}

std::unique_ptr<Chunk> JavaChunkHandle::get_chunk(std::optional<std::set<std::string>> component_ids)
{
    return get_java_chunk(component_ids);
}

void JavaChunkHandle::set_java_chunk(const JavaChunk& chunk)
{
    throw std::runtime_error("NotImplementedError");
}

void JavaChunkHandle::set_chunk(const Chunk& chunk)
{
    auto* java_chunk = dynamic_cast<const JavaChunk*>(&chunk);
    if (!java_chunk) {
        throw std::invalid_argument("chunk is not an instance of JavaChunk");
    }
    set_java_chunk(*java_chunk);
}

void JavaChunkHandle::delete_chunk()
{
    throw std::runtime_error("NotImplementedError");
}

} // namespace Amulet
