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
};

class SectionArrayMap {
private:
    SectionShape _array_shape;
    std::variant<std::uint32_t, std::shared_ptr<IndexArray3D>> _default_array;
    std::unordered_map<std::int64_t, std::shared_ptr<IndexArray3D>> _arrays;

public:
    AMULET_CORE_EXPORT SectionArrayMap(
        const SectionShape& array_shape,
        std::variant<std::uint32_t, std::shared_ptr<IndexArray3D>> default_array);

    AMULET_CORE_EXPORT void serialise(BinaryWriter&) const;
    AMULET_CORE_EXPORT static SectionArrayMap deserialise(BinaryReader&);

    AMULET_CORE_EXPORT const SectionShape& get_array_shape() const;
    AMULET_CORE_EXPORT std::variant<std::uint32_t, std::shared_ptr<IndexArray3D>> get_default_array() const;
    AMULET_CORE_EXPORT void set_default_array(std::variant<std::uint32_t, std::shared_ptr<IndexArray3D>> default_array);
    AMULET_CORE_EXPORT const std::unordered_map<std::int64_t, std::shared_ptr<IndexArray3D>>& get_arrays() const;
    AMULET_CORE_EXPORT size_t get_size() const;
    AMULET_CORE_EXPORT bool contains_section(std::int64_t cy) const;
    AMULET_CORE_EXPORT std::shared_ptr<IndexArray3D> get_section(std::int64_t cy) const;
    AMULET_CORE_EXPORT void set_section(std::int64_t cy, std::shared_ptr<IndexArray3D> section);
    AMULET_CORE_EXPORT void populate_section(std::int64_t cy);
    AMULET_CORE_EXPORT void del_section(std::int64_t cy);
};

} // namespace Amulet
