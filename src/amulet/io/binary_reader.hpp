#pragma once

#include <string>
#include <cstdint>
#include <cstring>
#include <algorithm>
#include <bit>
#include <functional>
#include <stdexcept>
#include <memory>

#include <amulet_nbt/io/binary_reader.hpp>


namespace Amulet {
    class BinaryReader: public AmuletNBT::BinaryReader {
    

    public:
        BinaryReader(
            const std::string& input,
            size_t& position
        ) : AmuletNBT::BinaryReader(input, position, std::endian::little, [](const std::string& value) {return value; }) {}

        std::string readSizeAndBytes() {
            std::uint64_t length;
            readNumericInto<std::uint64_t>(length);
            // Ensure the buffer is long enough
            if (position + length > data.size()) {
                throw std::out_of_range("Cannot read string of length " + std::to_string(length) + " at position " + std::to_string(position));
            }

            std::string value = data.substr(position, length);
            position += length;
            return value;
        }
    };

    template <class T>
    std::shared_ptr<T> deserialise(const std::string& data){
        size_t position = 0;
        BinaryReader reader(data, position);
        return T::deserialise(reader);
    }
}
