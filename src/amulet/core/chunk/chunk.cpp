#include <functional>
#include <memory>
#include <optional>
#include <string>
#include <unordered_map>

#include <amulet/utils/threading/mutex.hpp>
#include <amulet/utils/threading/shared_mutex.hpp>
#include <amulet/utils/threading/thread_safety.hpp>

#include <amulet/core/dll.hpp>

#include "chunk.hpp"

namespace Amulet {
namespace detail {

    class NullChunkConstructors {
    private:
        astd::shared_mutex mutex;
        std::unordered_map<std::string, detail::ChunkContructor> chunk_constructors ASTD_GUARDED_BY(mutex);

    public:
        void add_null_chunk_constructor(const std::string& id, ChunkContructor constructor) ASTD_EXCLUDES(mutex)
        {
            astd::lock_guard guard(mutex);
            if (chunk_constructors.contains(id)) {
                throw std::runtime_error("A chunk class has already been registered with ID " + id);
            }
            chunk_constructors.emplace(id, constructor);
        }

        void remove_null_chunk_constructor(const std::string& id) ASTD_EXCLUDES(mutex)
        {
            astd::lock_guard guard(mutex);
            chunk_constructors.erase(id);
        }

        std::shared_ptr<Chunk> get_null_chunk(std::string chunk_id) ASTD_EXCLUDES(mutex)
        {
            astd::shared_lock lock(mutex);
            return chunk_constructors.at(chunk_id)();
        }
    };

    static NullChunkConstructors& get_null_constructor_storage()
    {
        static NullChunkConstructors constructors;
        return constructors;
    }

    void add_null_chunk_constructor(const std::string& id, ChunkContructor constructor)
    {
        get_null_constructor_storage().add_null_chunk_constructor(id, std::move(constructor));
    }

    void remove_null_chunk_constructor(const std::string& id)
    {
        get_null_constructor_storage().remove_null_chunk_constructor(id);
    }

} // namespace detail

std::shared_ptr<Chunk> get_null_chunk(std::string chunk_id)
{
    detail::get_null_constructor_storage().get_null_chunk(chunk_id);
}

ChunkLoadError::~ChunkLoadError() noexcept { }
ChunkDoesNotExist::~ChunkDoesNotExist() noexcept { }

} // namespace Amulet
