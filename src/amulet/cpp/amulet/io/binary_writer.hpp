#pragma once

#include <iostream>
#include <string>
#include <cstdint>
#include <cstring>
#include <algorithm>
#include <bit>
#include <functional>


namespace Amulet {
    class BinaryWriter {
    private:
        std::string data;

    public:
        BinaryWriter() {}

        /**
         * Fix the endianness of the numeric value and write it to the buffer.
         */
        template <typename T> inline void writeNumeric(const T& value) {
            // Create
            char* src = (char*)&value;

            // Copy
            if (std::endian::big == std::endian::native){
                data.append(src, sizeof(T));
            } else {
                for (size_t i = 0; i < sizeof(T); i++){
                    data.push_back(src[sizeof(T) - i - 1]);
                }
            }
        }

        void writeString(const std::string& value) {
            writeNumeric<std::uint64_t>(value.size());
            data.append(value);
        }

        std::string getBuffer(){
            return data;
        }
    };
}
