#pragma once

#include <cstdint>
#include <map>
#include <memory>
#include <optional>
#include <stdexcept>
#include <string>

#include <amulet_nbt/tag/named_tag.hpp>

#include <amulet/dll.hpp>

namespace Amulet {
typedef std::map<std::string, std::shared_ptr<AmuletNBT::NamedTag>> JavaRawChunkType;

class JavaRawChunkComponent {
private:
    std::optional<std::shared_ptr<JavaRawChunkType>> _raw_data;

protected:
    // Null constructor
    JavaRawChunkComponent() { }
    // Default constructor
    void init(std::shared_ptr<JavaRawChunkType> raw_data) { _raw_data = raw_data; }
    void init() { _raw_data = std::make_shared<JavaRawChunkType>(); }
    // Serialise the component data
    AMULET_CORE_EXPORT std::optional<std::string> serialise() const;
    // Deserialise the component
    AMULET_CORE_EXPORT void deserialise(std::optional<std::string>);

public:
    AMULET_CORE_EXPORT static const std::string ComponentID;
    std::shared_ptr<JavaRawChunkType> get_raw_data()
    {
        if (_raw_data) {
            return *_raw_data;
        }
        throw std::runtime_error("JavaRawChunkComponent has not been loaded.");
    }
    void set_raw_data(std::shared_ptr<JavaRawChunkType> raw_data)
    {
        if (_raw_data) {
            _raw_data = raw_data;
        } else {
            throw std::runtime_error("JavaRawChunkComponent has not been loaded.");
        }
    }
};
}
