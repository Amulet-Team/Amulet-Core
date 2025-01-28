#pragma once

#include <algorithm>
#include <bit>
#include <cstdint>
#include <cstring>
#include <functional>
#include <string>

#include <amulet_nbt/io/binary_writer.hpp>

namespace Amulet {
class BinaryWriter : public AmuletNBT::BinaryWriter {
public:
    BinaryWriter()
        : AmuletNBT::BinaryWriter(std::endian::little, [](const std::string& value) { return value; })
    {
    }

    void writeSizeAndBytes(const std::string& value)
    {
        writeNumeric<std::uint64_t>(value.size());
        data.append(value);
    }
};

template <typename T>
std::string serialise(const T& obj)
{
    BinaryWriter writer;
    obj.serialise(writer);
    return writer.getBuffer();
}
}
