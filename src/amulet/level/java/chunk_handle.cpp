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
    } else if (data[0] == 'e') {
        // 1 followed by the string if other error.
        throw ChunkLoadError(data.substr(1));
    } else if (data[0] == 'c') {
        // 0 followed by the chunk id if a valid chunk.
        return detail::get_java_null_chunk(data.substr(1));
    } else {
        throw std::runtime_error("Invalid chunk id prefix.");
    }
}

void JavaChunkHandle::_preload() {
    if (_chunk_history->has_resource(_key)) {
        // Do nothing if the resource already exists.
        return;
    }

    // Get the chunk data.
    JavaRawChunk raw_chunk;
    try {
        raw_chunk = _raw_dimension->get_raw_chunk(_cx, _cz);
    } catch (const ChunkDoesNotExist&) {
        _chunk_history->set_initial_value(_key, "");
        return;
    }

    // Decode the chunk.
    std::unique_ptr<JavaChunk> chunk;
    try {
        chunk = _raw_dimension->decode_chunk(raw_chunk, _cx, _cz);
    } catch (const ChunkLoadError& e) {
        _chunk_history->set_initial_value(_key, 'e' + std::string(e.what()));
        return;
    }

    // Save the chunk.
    _chunk_history->set_initial_value(_key, 'c' + detail::get_java_chunk_id(*chunk));
    for (const auto& [component_id, component_data] : chunk->serialise_chunk()) {
        if (!component_data) {
            throw std::runtime_error("Component " + component_id + " cannot be undefined when initialising chunk");
        }
        _chunk_data_history->set_initial_value(std::string(_key) + '/' + component_id, *component_data);
    }
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
        // Load the chunk if it wasn't previously populated.
        _preload();
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
    std::lock_guard lock(_chunk_history->get_mutex());

    // Set initial state.
    if (true) {
        // TODO: set above to history_enabled
        _preload();
    } else if (!_chunk_history->has_resource(_key)) {
        _chunk_history->set_initial_value(_key, "");
    }

    auto old_chunk_id = _chunk_history->get_value(_key);
    auto new_chunk_id = 'c' + detail::get_java_chunk_id(chunk);

    auto component_data = chunk.serialise_chunk();
    std::list<std::pair<std::string, std::string>> values;

    auto copy_values = [&]<bool error_undefined>() {
        for (const auto& [component_id, data] : component_data) {
            if (data) {
                values.emplace_back(std::string(_key) + '/' + component_id, *data);
            } else if constexpr (error_undefined) {
                throw std::runtime_error("When changing chunk class all the data must be present.");
            }
        }
    };

    // Copy defined values.
    if (old_chunk_id != new_chunk_id) {
        // Error if any component is undefined
        copy_values.operator()<true>();
    } else {
        // Remove undefined components.
        copy_values.operator()<false>();
    }

    // Set new state.
    _chunk_history->set_value(_key, new_chunk_id);
    if (!values.empty()) {
        _chunk_data_history->set_values(values, true);
    }
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
    std::lock_guard lock(_chunk_history->get_mutex());

    // Set initial state.
    if (true) {
        // TODO: set above to history_enabled
        _preload();
    } else if (!_chunk_history->has_resource(_key)) {
        _chunk_history->set_initial_value(_key, "");
    }

    // Delete
    _chunk_history->set_value(_key, "");
}

} // namespace Amulet
