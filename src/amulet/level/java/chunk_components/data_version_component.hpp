#pragma once

#include <cstdint>
#include <optional>
#include <stdexcept>
#include <string>

#include <amulet/dll.hpp>

namespace Amulet {
class DataVersionComponent {
private:
    std::optional<std::int64_t> _data_version;

protected:
    // Null constructor
    DataVersionComponent() { }
    // Default constructor
    void init(std::int64_t data_version) { _data_version = data_version; }
    // Serialise the component data
    AMULET_CORE_EXPORT std::optional<std::string> serialise() const;
    // Deserialise the component
    AMULET_CORE_EXPORT void deserialise(std::optional<std::string>);

public:
    AMULET_CORE_EXPORT static const std::string ComponentID;
    std::int64_t get_data_version()
    {
        if (_data_version) {
            return *_data_version;
        }
        throw std::runtime_error("DataVersionComponent has not been loaded.");
    }
};
}
