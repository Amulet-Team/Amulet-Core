#pragma once

#include <iostream>
#include <string>
#include <cstdint>
#include <cstring>
#include <algorithm>
#include <bit>
#include <functional>
#include <stdexcept>


namespace Amulet {
    class BinaryReader {
    private:
        const std::string& data;
        size_t& position;

    public:
        BinaryReader(
            const std::string& input,
            size_t& position
        )
            : data(input), position(position) {}

        /**
         * Read a numeric type from the buffer into the given value and fix its endianness.
         */
        template <typename T> inline void readNumericInto(T& value) {
            // Ensure the buffer is long enough
            if (position + sizeof(T) > data.size()) {
                throw std::out_of_range(std::string("Cannot read ") + typeid(T).name() + " at position " + std::to_string(position));
            }

            // Create
            const char* src = &data[position];
            char* dst = (char*)&value;

            // Copy
            if (std::endian::big == std::endian::native){
                for (size_t i = 0; i < sizeof(T); i++){
                    dst[i] = src[i];
                }
            } else {
                for (size_t i = 0; i < sizeof(T); i++){
                    dst[i] = src[sizeof(T) - i - 1];
                }
            }

            // Increment position
            position += sizeof(T);
        }

        /**
         * Read a numeric type from the buffer and fix its endianness.
         *
         * @return A value of the requested type.
         */
        template <typename T> inline T readNumeric() {
            T value;
            readNumericInto<T>(value);
            return value;
        }

        std::string readString() {
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

        size_t getPosition(){
            return position;
        }

        bool has_more_data(){
            return position < data.size();
        }
    };

    template <typename T>
    T deserialise(const std::string& data){
        size_t position = 0;
        BinaryReader reader(data, position);
        return T::deserialise(reader);
    }
}
