#pragma once

#include <optional>
#include <cstdint>
#include <string>
#include <stdexcept>


namespace Amulet {
	class DataVersionComponent {
	private:
		std::optional<std::int64_t> _data_version;
	protected:
		// Null constructor
		DataVersionComponent() {};
		// Default constructor
		void init(std::int64_t data_version) { _data_version = data_version; }
		// Serialise the component data
		std::optional<std::string> serialise() const;
		// Deserialise the component
		void deserialise(std::optional<std::string>);
	public:
		static const std::string ComponentID;
		std::int64_t get_data_version() {
			if (_data_version) {
				return *_data_version;
			}
			throw std::runtime_error("DataVersionComponent has not been loaded.");
		};
	};
}
