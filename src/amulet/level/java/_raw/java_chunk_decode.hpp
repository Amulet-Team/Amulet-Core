#pragma once
#include <memory>
#include <map>
#include <cstdint>

#include <pybind11/pybind11.h>

#include <amulet_nbt/tag/named_tag.hpp>

#include <amulet/chunk.hpp>
#include <amulet/level/java/java_chunk.hpp>

namespace py = pybind11;

namespace Amulet {
	std::shared_ptr<Amulet::JavaChunk> decode_java_chunk(
		py::object raw_level,
		py::object dimension,
		std::map<std::string, AmuletNBT::NamedTag>& raw_chunk,
		std::int64_t cx,
		std::int64_t cz
	);
}
