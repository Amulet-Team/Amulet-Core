#include <string>

#include <amulet/dll.hpp>
#include <amulet/io/binary_reader.hpp>
#include <amulet/io/binary_writer.hpp>

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
    std::memcpy(_buffer, other._buffer, sizeof(std::uint32_t) * other.get_size());
}

IndexArray3D::~IndexArray3D() {
    free(_buffer);
}

void IndexArray3D::serialise(BinaryWriter& writer) const
{
    writer.writeNumeric<std::uint8_t>(1);

    // Write array shape
    const auto& array_shape = get_shape();
    writer.writeNumeric<std::uint16_t>(std::get<0>(array_shape));
    writer.writeNumeric<std::uint16_t>(std::get<1>(array_shape));
    writer.writeNumeric<std::uint16_t>(std::get<2>(array_shape));

    // Write array
    const auto& size = get_size();
    const auto* buffer = get_buffer();
    for (auto i = 0; i < size; i++) {
        writer.writeNumeric<std::uint32_t>(buffer[i]);
    }
}
std::shared_ptr<IndexArray3D> IndexArray3D::deserialise(BinaryReader& reader)
{
    auto version = reader.readNumeric<std::uint8_t>();
    switch (version) {
    case 1: {
        // Read array shape
        auto array_shape = std::make_tuple(
            reader.readNumeric<std::uint16_t>(),
            reader.readNumeric<std::uint16_t>(),
            reader.readNumeric<std::uint16_t>());

        // Construct instance
        auto self = std::make_shared<IndexArray3D>(array_shape);

        // Read array
        const auto& size = self->get_size();
        auto* buffer = self->get_buffer();
        for (auto i = 0; i < size; i++) {
            buffer[i] = reader.readNumeric<std::uint32_t>();
        }

        return self;
    }
    default:
        throw std::invalid_argument("Unsupported IndexArray3D version " + std::to_string(version));
    }
}

const SectionShape& IndexArray3D::get_shape() const
{
    return _shape;
}
const size_t& IndexArray3D::get_size() const { return _size; }
std::uint32_t* IndexArray3D::get_buffer() const { return _buffer; }

static inline void validate_array_shape(
    const std::shared_ptr<IndexArray3D>& default_array,
    const SectionShape& array_shape)
{
    if (default_array->get_shape() != array_shape) {
        throw std::invalid_argument("Array shape does not match required shape.");
    }
}

static inline void validate_array_shape(
    const std::variant<std::uint32_t, std::shared_ptr<IndexArray3D>>& default_array,
    const SectionShape& array_shape)
{
    if (std::holds_alternative<std::shared_ptr<IndexArray3D>>(default_array)) {
        validate_array_shape(std::get<std::shared_ptr<IndexArray3D>>(default_array), array_shape);
    }
}

// SectionArrayMap
SectionArrayMap::SectionArrayMap(
    const SectionShape& array_shape,
    std::variant<std::uint32_t, std::shared_ptr<IndexArray3D>> default_array)
    : _array_shape(array_shape)
    , _default_array(default_array)
    , _arrays()
{
    validate_array_shape(_default_array, _array_shape);
}

void SectionArrayMap::serialise(BinaryWriter& writer) const
{
    writer.writeNumeric<std::uint8_t>(1);

    // Write array shape
    const auto& array_shape = get_array_shape();
    writer.writeNumeric<std::uint16_t>(std::get<0>(array_shape));
    writer.writeNumeric<std::uint16_t>(std::get<1>(array_shape));
    writer.writeNumeric<std::uint16_t>(std::get<2>(array_shape));

    // Write default array
    std::visit(
        [&writer](auto&& arg) {
            using T = std::decay_t<decltype(arg)>;
            if constexpr (std::is_same_v<T, std::uint32_t>) {
                writer.writeNumeric<std::uint8_t>(0);
                writer.writeNumeric<std::uint32_t>(arg);
            } else {
                writer.writeNumeric<std::uint8_t>(1);
                arg->serialise(writer);
            }
        },
        get_default_array());

    // Write arrays
    const auto& arrays = get_arrays();
    writer.writeNumeric<std::uint64_t>(arrays.size());
    for (const auto& [cy, arr] : arrays) {
        writer.writeNumeric<std::int64_t>(cy);
        arr->serialise(writer);
    }
}
std::shared_ptr<SectionArrayMap> SectionArrayMap::deserialise(BinaryReader& reader)
{
    auto version = reader.readNumeric<std::uint8_t>();
    switch (version) {
    case 1: {
        // Read array shape
        auto array_shape = std::make_tuple(
            reader.readNumeric<std::uint16_t>(),
            reader.readNumeric<std::uint16_t>(),
            reader.readNumeric<std::uint16_t>());

        // Read default array
        auto default_array_state = reader.readNumeric<std::uint8_t>();
        std::variant<std::uint32_t, std::shared_ptr<IndexArray3D>> default_array;
        switch (default_array_state) {
        case 0:
            default_array = reader.readNumeric<std::uint32_t>();
            break;
        case 1:
            default_array = IndexArray3D::deserialise(reader);
            break;
        default:
            throw std::invalid_argument("Invalid default array state value " + std::to_string(default_array_state));
        }

        // Construct instance
        auto self = std::make_shared<SectionArrayMap>(array_shape, default_array);

        // Populate arrays
        auto array_count = reader.readNumeric<std::uint64_t>();
        for (auto i = 0; i < array_count; i++) {
            auto cy = reader.readNumeric<std::int64_t>();
            self->set_section(cy, IndexArray3D::deserialise(reader));
        }

        return self;
    }
    default:
        throw std::invalid_argument("Unsupported BlockComponentData version " + std::to_string(version));
    }
}

const SectionShape& SectionArrayMap::get_array_shape() const { return _array_shape; }

std::variant<std::uint32_t, std::shared_ptr<IndexArray3D>> SectionArrayMap::get_default_array() const
{
    return _default_array;
}

void SectionArrayMap::set_default_array(std::variant<std::uint32_t, std::shared_ptr<IndexArray3D>> default_array)
{
    validate_array_shape(default_array, _array_shape);
    _default_array = default_array;
}

const std::unordered_map<std::int64_t, std::shared_ptr<IndexArray3D>>& SectionArrayMap::get_arrays() const
{
    return _arrays;
}

size_t SectionArrayMap::get_size() const { return _arrays.size(); }

bool SectionArrayMap::contains_section(std::int64_t cy) const
{
    return _arrays.contains(cy);
}

std::shared_ptr<IndexArray3D> SectionArrayMap::get_section(std::int64_t cy) const
{
    return _arrays.at(cy);
}

void SectionArrayMap::set_section(std::int64_t cy, std::shared_ptr<IndexArray3D> section)
{
    validate_array_shape(section, _array_shape);
    _arrays[cy] = section;
}

void SectionArrayMap::populate_section(std::int64_t cy)
{
    if (_arrays.contains(cy)) {
        return;
    }
    std::visit([this, &cy](auto&& arg) {
        using T = std::decay_t<decltype(arg)>;
        if constexpr (std::is_same_v<T, std::uint32_t>) {
            _arrays[cy] = std::make_shared<IndexArray3D>(_array_shape, arg);
        } else {
            _arrays[cy] = std::make_shared<IndexArray3D>(*arg);
        }
    },
        _default_array);
}

void SectionArrayMap::del_section(std::int64_t cy)
{
    _arrays.erase(cy);
}

} // namespace Amulet
