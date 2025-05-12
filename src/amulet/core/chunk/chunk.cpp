#include <functional>
#include <memory>
#include <optional>
#include <shared_mutex>
#include <string>
#include <unordered_map>

#include <amulet/core/dll.hpp>

#include "chunk.hpp"

namespace Amulet {
namespace detail {

    static std::shared_mutex& get_chunk_constructors_mutex()
    {
        static std::shared_mutex chunk_constructors_mutex;
        return chunk_constructors_mutex;
    }

    static std::unordered_map<std::string, detail::ChunkContructor>& get_chunk_constructors()
    {
        static std::unordered_map<std::string, detail::ChunkContructor> chunk_constructors;
        return chunk_constructors;
    }

    void add_null_chunk_constructor(const std::string& id, ChunkContructor constructor)
    {
        std::lock_guard guard(get_chunk_constructors_mutex());
        auto& chunk_constructors = get_chunk_constructors();
        if (chunk_constructors.contains(id)) {
            throw std::runtime_error("A chunk class has already been registered with ID " + id);
        }
        chunk_constructors.emplace(id, constructor);
    }
    void remove_null_chunk_constructor(const std::string& id)
    {
        std::lock_guard guard(get_chunk_constructors_mutex());
        get_chunk_constructors().erase(id);
    }

} // namespace detail

std::shared_ptr<Chunk> get_null_chunk(std::string chunk_id)
{
    std::shared_lock lock(detail::get_chunk_constructors_mutex());
    return detail::get_chunk_constructors().at(chunk_id)();
}

} // namespace Amulet
