#pragma once

#include <iostream>
#include <string>
#include <cstdint>
#include <cstring>
#include <algorithm>
#include <bit>
#include <functional>

#include <amulet_nbt/io/binary_writer.hpp>


namespace Amulet {
    namespace detail {
        std::string encode_null(const std::string& value) { return value; }
    }

    class BinaryWriter: public AmuletNBT::BinaryWriter {
        public:
            BinaryWriter(): AmuletNBT::BinaryWriter(std::endian::big, detail::encode_null) {}

            void writeSizeAndBytes(const std::string& value) {
                writeNumeric<std::uint64_t>(value.size());
                data.append(value);
            }
    };

    template <typename T>
    std::string serialise(const T& obj){
        BinaryWriter writer;
        obj.serialise(writer);
        return writer.getBuffer();
    }
}
