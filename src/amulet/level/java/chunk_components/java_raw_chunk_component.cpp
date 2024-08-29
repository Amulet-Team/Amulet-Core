#include <amulet/level/java/chunk_components/java_raw_chunk_component.hpp>

namespace Amulet {
	const std::string JavaRawChunkComponent::ComponentID = "Amulet::JavaRawChunkComponent";

	std::optional<std::string> JavaRawChunkComponent::serialise() const {
		throw std::runtime_error("NotImplemented");
	}
	void JavaRawChunkComponent::deserialise(std::optional<std::string>) {
		throw std::runtime_error("NotImplemented");
	}
}
