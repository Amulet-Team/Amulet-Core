#include <string>

#include <amulet/io/binary_reader.hpp>
#include <amulet/io/binary_writer.hpp>

#include <amulet/core/dll.hpp>

#include "section_array_map.hpp"

namespace Amulet {

template <typename T>
T* new_buffer(size_t count)
{
    T* buffer = static_cast<T*>(std::malloc(sizeof(T) * count));
    if (buffer == nullptr) {
        throw std::runtime_error("Could not allocate buffer");
    }
    return buffer;
}

// IndexArray3D
IndexArray3D::IndexArray3D(const SectionShape& shape)
    : _shape(shape)
    , _size(std::get<0>(shape) * std::get<1>(shape) * std::get<2>(shape))
    , _buffer(new_buffer<std::uint32_t>(_size))
{
}

IndexArray3D::IndexArray3D(const SectionShape& shape, std::uint32_t value)
    : IndexArray3D(shape)
{
    std::fill_n(_buffer, _size, value);
}

IndexArray3D::IndexArray3D(const IndexArray3D& other)
    : IndexArray3D(other.get_shape())
{
    std::memcpy(_buffer, other._buffer, sizeof(std::uint32_t) * _size);
}

IndexArray3D::IndexArray3D(IndexArray3D&& other) noexcept
    : _shape(other._shape)
    , _size(other._size)
    , _buffer(other._buffer)
{
    other._buffer = nullptr;
}

IndexArray3D& IndexArray3D::operator=(const IndexArray3D& other)
{
    if (_buffer == nullptr) {
        // Buffer was freed. Create a new one.
        _buffer = new_buffer<std::uint32_t>(other.get_size());
    } else if (_size != other.get_size()) {
        // Buffer size has changed. Free and create a new one.
        free(_buffer);
        _buffer = new_buffer<std::uint32_t>(other.get_size());
    }
    _shape = other._shape;
    _size = other._size;
    std::memcpy(_buffer, other._buffer, sizeof(std::uint32_t) * _size);
    return *this;
}

IndexArray3D& IndexArray3D::operator=(IndexArray3D&& other) noexcept
{
    if (_buffer != nullptr) {
        free(_buffer);
    }
    _shape = other._shape;
    _size = other._size;
    _buffer = other._buffer;
    other._buffer = nullptr;
    return *this;
}

IndexArray3D::~IndexArray3D()
{
    if (_buffer != nullptr) {
        free(_buffer);
    }
}

void IndexArray3D::serialise(BinaryWriter& writer) const
{
    writer.write_numeric<std::uint8_t>(1);

    // Write array shape
    const auto& array_shape = get_shape();
    writer.write_numeric<std::uint16_t>(std::get<0>(array_shape));
    writer.write_numeric<std::uint16_t>(std::get<1>(array_shape));
    writer.write_numeric<std::uint16_t>(std::get<2>(array_shape));

    // Write array
    const auto& size = get_size();
    const auto* buffer = get_buffer();
    for (auto i = 0; i < size; i++) {
        writer.write_numeric<std::uint32_t>(buffer[i]);
    }
}
IndexArray3D IndexArray3D::deserialise(BinaryReader& reader)
{
    auto version = reader.read_numeric<std::uint8_t>();
    switch (version) {
    case 1: {
        // Read array shape
        auto array_shape = std::make_tuple(
            reader.read_numeric<std::uint16_t>(),
            reader.read_numeric<std::uint16_t>(),
            reader.read_numeric<std::uint16_t>());

        // Construct instance
        IndexArray3D self(array_shape);

        // Read array
        const auto& size = self.get_size();
        auto* buffer = self.get_buffer();
        for (auto i = 0; i < size; i++) {
            buffer[i] = reader.read_numeric<std::uint32_t>();
        }

        return self;
    }
    default:
        throw std::invalid_argument("Unsupported IndexArray3D version " + std::to_string(version));
    }
}

// SectionArrayMap
void SectionArrayMap::serialise(BinaryWriter& writer) const
{
    writer.write_numeric<std::uint8_t>(1);

    // Write array shape
    const auto& array_shape = get_array_shape();
    writer.write_numeric<std::uint16_t>(std::get<0>(array_shape));
    writer.write_numeric<std::uint16_t>(std::get<1>(array_shape));
    writer.write_numeric<std::uint16_t>(std::get<2>(array_shape));

    // Write default array
    std::visit(
        [&writer](auto&& arg) {
            using T = std::decay_t<decltype(arg)>;
            if constexpr (std::is_same_v<T, std::uint32_t>) {
                writer.write_numeric<std::uint8_t>(0);
                writer.write_numeric<std::uint32_t>(arg);
            } else {
                writer.write_numeric<std::uint8_t>(1);
                arg->serialise(writer);
            }
        },
        get_default_array());

    // Write arrays
    const auto& arrays = get_arrays();
    writer.write_numeric<std::uint64_t>(arrays.size());
    for (const auto& [cy, arr] : arrays) {
        writer.write_numeric<std::int64_t>(cy);
        arr->serialise(writer);
    }
}

SectionArrayMap SectionArrayMap::deserialise(BinaryReader& reader)
{
    auto version = reader.read_numeric<std::uint8_t>();
    switch (version) {
    case 1: {
        // Read array shape
        auto array_shape = std::make_tuple(
            reader.read_numeric<std::uint16_t>(),
            reader.read_numeric<std::uint16_t>(),
            reader.read_numeric<std::uint16_t>());

        // Read default array
        auto default_array_state = reader.read_numeric<std::uint8_t>();
        std::variant<std::uint32_t, std::shared_ptr<IndexArray3D>> default_array;
        switch (default_array_state) {
        case 0:
            default_array = reader.read_numeric<std::uint32_t>();
            break;
        case 1:
            default_array = std::make_shared<IndexArray3D>(Amulet::deserialise<IndexArray3D>(reader));
            break;
        default:
            throw std::invalid_argument("Invalid default array state value " + std::to_string(default_array_state));
        }

        // Construct instance
        SectionArrayMap self(array_shape, default_array);

        // Populate arrays
        auto array_count = reader.read_numeric<std::uint64_t>();
        for (auto i = 0; i < array_count; i++) {
            auto cy = reader.read_numeric<std::int64_t>();
            self.set_section(cy, std::make_shared<IndexArray3D>(Amulet::deserialise<IndexArray3D>(reader)));
        }

        return self;
    }
    default:
        throw std::invalid_argument("Unsupported BlockComponentData version " + std::to_string(version));
    }
}

void SectionArrayMap::populate_section(std::int64_t cy)
{
    if (_arrays.contains(cy)) {
        return;
    }
    std::visit(
        [this, &cy](auto&& arg) {
            using T = std::decay_t<decltype(arg)>;
            if constexpr (std::is_same_v<T, std::uint32_t>) {
                _arrays.emplace(cy, std::make_shared<IndexArray3D>(_array_shape, arg));
            } else {
                _arrays.emplace(cy, std::make_shared<IndexArray3D>(*arg));
            }
        },
        _default_array);
}

} // namespace Amulet
