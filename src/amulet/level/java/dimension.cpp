#include "dimension.hpp"
#include "chunk_handle.hpp"

namespace Amulet {

JavaDimension::JavaDimension(
    std::shared_ptr<JavaRawDimension> raw_dimension,
    HistoryManager& history_manager,
    std::shared_ptr<bool> history_enabled)
    : _raw_dimension(std::move(raw_dimension))
    , _chunk_history(history_manager.new_layer<detail::ChunkKey>())
    , _chunk_data_history(history_manager.new_layer<std::string>())
    , _history_enabled(std::move(history_enabled))
{
}

JavaDimension::~JavaDimension()
{
}

const DimensionID& JavaDimension::get_dimension_id() const
{
    return _raw_dimension->get_dimension_id();
}

std::variant<SelectionBox, SelectionGroup> JavaDimension::get_bounds() const
{
    return _raw_dimension->get_bounds();
}

const BlockStack& JavaDimension::get_default_block() const
{
    return _raw_dimension->get_default_block();
}

const Biome& JavaDimension::get_default_biome() const
{
    return _raw_dimension->get_default_biome();
}

std::shared_ptr<JavaChunkHandle> JavaDimension::get_java_chunk_handle(std::int64_t cx, std::int64_t cz)
{
    auto key = std::make_pair(cx, cz);
    {
        std::shared_lock handle_lock(_chunk_handles_mutex);
        auto it = _chunk_handles.find(key);
        if (it != _chunk_handles.end()) {
            auto chunk_handle = it->second.lock();
            if (chunk_handle) {
                return chunk_handle;
            }
        }
    }
    {
        std::lock_guard handle_lock(_chunk_handles_mutex);
        auto it = _chunk_handles.find(key);
        if (it == _chunk_handles.end()) {
            auto chunk_handle = std::shared_ptr<JavaChunkHandle>(
                new JavaChunkHandle(
                    get_dimension_id(),
                    cx,
                    cz,
                    _raw_dimension,
                    _chunk_history,
                    _chunk_data_history,
                    _history_enabled));
            _chunk_handles.emplace(key, chunk_handle);
            return chunk_handle;
        } else {
            auto chunk_handle = it->second.lock();
            if (!chunk_handle) {
                auto chunk_handle = std::shared_ptr<JavaChunkHandle>(
                    new JavaChunkHandle(
                        get_dimension_id(),
                        cx,
                        cz,
                        _raw_dimension,
                        _chunk_history,
                        _chunk_data_history,
                        _history_enabled));
                it->second = chunk_handle;
            }
            return chunk_handle;
        }
    }
}

std::shared_ptr<ChunkHandle> JavaDimension::get_chunk_handle(std::int64_t cx, std::int64_t cz)
{
    return get_java_chunk_handle(cx, cz);
}

} // namespace Amulet
