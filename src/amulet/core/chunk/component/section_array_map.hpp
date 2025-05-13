#pragma once

#include <cstdint>
#include <cstdlib>
#include <memory>
#include <span>
#include <stdexcept>
#include <tuple>
#include <type_traits>
#include <unordered_map>
#include <variant>
#include <vector>

#include <amulet/io/binary_reader.hpp>
#include <amulet/io/binary_writer.hpp>

#include <amulet/core/dll.hpp>

namespace Amulet {

typedef std::tuple<std::uint16_t, std::uint16_t, std::uint16_t> SectionShape;

class IndexArray3D {
private:
    SectionShape _shape;
    size_t _size;
    std::uint32_t* _buffer;

public:
    AMULET_CORE_EXPORT IndexArray3D(const SectionShape& shape);
    AMULET_CORE_EXPORT IndexArray3D(const SectionShape& shape, std::uint32_t value);

    AMULET_CORE_EXPORT IndexArray3D(const IndexArray3D& other);
    AMULET_CORE_EXPORT IndexArray3D(IndexArray3D&& other) noexcept;
    AMULET_CORE_EXPORT IndexArray3D& operator=(const IndexArray3D& other);
    AMULET_CORE_EXPORT IndexArray3D& operator=(IndexArray3D&& other) noexcept;

    AMULET_CORE_EXPORT ~IndexArray3D();

    AMULET_CORE_EXPORT void serialise(BinaryWriter&) const;
    AMULET_CORE_EXPORT static IndexArray3D deserialise(BinaryReader&);

    const SectionShape& get_shape() const { return _shape; }
    const size_t& get_size() const { return _size; }
    std::uint32_t* get_buffer() const { return _buffer; }
    std::span<std::uint32_t> get_span() const { return { _buffer, _size }; }
};

class SectionArrayMap {
private:
    SectionShape _array_shape;
    std::variant<std::uint32_t, std::shared_ptr<IndexArray3D>> _default_array;
    std::unordered_map<std::int64_t, std::shared_ptr<IndexArray3D>> _arrays;

    void validate_array_shape(const IndexArray3D& array)
    {
        if (_array_shape != array.get_shape()) {
            throw std::invalid_argument("Array shape does not match stored shape.");
        }
    }

    void validate_array_shape(
        const std::variant<std::uint32_t, std::shared_ptr<IndexArray3D>>& array)
    {
        if (auto* arr = std::get_if<std::shared_ptr<IndexArray3D>>(&array)) {
            return validate_array_shape(**arr);
        }
    }

public:
    template <typename DefaultArrayT>
    SectionArrayMap(
        const SectionShape& array_shape,
        DefaultArrayT&& default_array)
        : _array_shape(array_shape)
        , _default_array(std::forward<DefaultArrayT>(default_array))
        , _arrays()
    {
        validate_array_shape(_default_array);
    }

    AMULET_CORE_EXPORT void serialise(BinaryWriter&) const;
    AMULET_CORE_EXPORT static SectionArrayMap deserialise(BinaryReader&);

    const SectionShape& get_array_shape() const { return _array_shape; }

    std::variant<std::uint32_t, std::shared_ptr<IndexArray3D>> get_default_array() const
    {
        return _default_array;
    }

    void set_default_array(std::variant<std::uint32_t, std::shared_ptr<IndexArray3D>> default_array)
    {
        validate_array_shape(default_array);
        _default_array = std::move(default_array);
    }

    const std::unordered_map<std::int64_t, std::shared_ptr<IndexArray3D>>& get_arrays() const
    {
        return _arrays;
    }

    size_t get_size() const { return _arrays.size(); }

    bool contains_section(std::int64_t cy) const
    {
        return _arrays.contains(cy);
    }

    std::shared_ptr<IndexArray3D> get_section(std::int64_t cy) const
    {
        return _arrays.at(cy);
    }

    void set_section(std::int64_t cy, std::shared_ptr<IndexArray3D> section)
    {
        validate_array_shape(*section);
        _arrays.insert_or_assign(cy, std::move(section));
    }

    AMULET_CORE_EXPORT void populate_section(std::int64_t cy);

    void del_section(std::int64_t cy)
    {
        _arrays.erase(cy);
    }
};

} // namespace Amulet
