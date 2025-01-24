#include <pybind11/pybind11.h>

#include <memory>
#include <map>
#include <cstdint>
#include <stdexcept>

#include <pybind11_extensions/builtins.hpp>

#include <amulet_nbt/tag/named_tag.hpp>

#include <amulet/chunk.hpp>
#include <amulet/level/java/java_chunk.hpp>

namespace py = pybind11;

namespace Amulet {
	std::map<std::string, AmuletNBT::NamedTag> encode_java_chunk(
		pybind11_extensions::PyObjectStr<"amulet.level.abc.Level"> raw_level,
		pybind11_extensions::PyObjectStr<"amulet.level.abc.Dimension"> dimension,
		std::shared_ptr<Amulet::JavaChunk> chunk,
		std::int64_t cx,
		std::int64_t cz
	) {
		throw std::runtime_error("");
	}
}
