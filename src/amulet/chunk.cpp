#include <functional>
#include <memory>
#include <optional>
#include <string>
#include <unordered_map>

#include <amulet/chunk.hpp>
#include <amulet/dll.hpp>

namespace Amulet {
namespace detail {
    std::unordered_map<std::string, std::function<std::shared_ptr<Chunk>()>>& get_chunk_constructors()
    {
        static std::unordered_map<std::string, std::function<std::shared_ptr<Chunk>()>> chunk_constructors;
        return chunk_constructors;
    }

}
std::shared_ptr<Chunk> get_null_chunk(std::string chunk_id)
{
    return detail::get_chunk_constructors().at(chunk_id)();
}
}
