#include <string>
#include <unordered_map>
#include <optional>
#include <functional>
#include <memory>

#include <amulet/chunk.hpp>

namespace Amulet {
	namespace detail {
		std::unordered_map<std::string, std::function<std::shared_ptr<Chunk>()>> chunk_constructors;
	}
	std::shared_ptr<Chunk> get_null_chunk(std::string chunk_id) {
		return detail::chunk_constructors.at(chunk_id)();
	}
}
