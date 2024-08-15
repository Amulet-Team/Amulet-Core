#include <amulet/chunk_components/block_component.hpp>

namespace Amulet {
	const std::string BlockComponent::ComponentID = "Amulet::BlockComponent";

	std::optional<std::string> BlockComponent::serialise() {
		throw std::runtime_error("NotImplemented");
	}
	void BlockComponent::deserialise(std::optional<std::string>) {
		throw std::runtime_error("NotImplemented");
	}
}
