#include <amulet/level/java/chunk_components/data_version.hpp>

namespace Amulet {
	const std::string DataVersionComponent::ComponentID = "Amulet::DataVersionComponent";

	std::optional<std::string> DataVersionComponent::serialise() {
		throw std::runtime_error("NotImplemented");
	}
	void DataVersionComponent::deserialise(std::optional<std::string>) {
		throw std::runtime_error("NotImplemented");
	}
}
