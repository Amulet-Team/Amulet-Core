#include <span>
#include <cmath>
#include <string>
#include <variant>
#include <algorithm>
#include <bit>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>

#include "long_array.hpp"

namespace py = pybind11;


template <typename decodedT>
py::array_t<decodedT> _decode_long_array(
    size_t size,
    std::uint8_t bits_per_entry,
    bool dense,
    const std::span<std::uint64_t>& encoded_span
) {
    // create the decoded array
    py::array_t<decodedT> decoded_arr(size);
    py::buffer_info decoded_buffer_info = decoded_arr.request();
    // Get the decoded array as a span
    std::span<decodedT> decoded_span(
        static_cast<decodedT*>(decoded_buffer_info.ptr),
        decoded_buffer_info.size
    );
    Amulet::decode_long_array(
        encoded_span,
        decoded_span,
        bits_per_entry,
        dense
    );
    return decoded_arr;
}

template <typename decodedT>
py::array_t<std::uint64_t> _encode_long_array(
    const py::buffer_info& decoded_buffer_info,
    std::variant<std::monostate, std::uint8_t> bits_per_entry_union,
    bool dense,
    std::uint8_t min_bits_per_entry
) {
    // Get the input array as a span
    const std::span<decodedT> decoded_span(
        static_cast<decodedT*>(decoded_buffer_info.ptr),
        decoded_buffer_info.size
    );
    // Get the number of bits to encode with
    std::uint8_t bits_per_entry = std::visit([&](auto&& arg) {
        using T = std::decay_t<decltype(arg)>;
        if constexpr (std::is_same_v<T, std::monostate>) {
            // If None compute it
            std::uint8_t required_bits_per_entry = std::bit_width(*std::max_element(decoded_span.begin(), decoded_span.end()));
            return std::max(
                min_bits_per_entry,
                required_bits_per_entry
            );
        }
        else {
            // If a value is given then use that.
            return arg;
        }
    }, bits_per_entry_union);
    
    // create the encoded array
    py::array_t<std::uint64_t> encoded_arr(Amulet::encoded_long_array_size(decoded_span.size(), bits_per_entry, dense));
    py::buffer_info encoded_buffer_info = encoded_arr.request();
    // Get the encoded array as a span
    std::span<std::uint64_t> encoded_span(
        static_cast<std::uint64_t*>(encoded_buffer_info.ptr),
        encoded_buffer_info.size
    );
    Amulet::encode_long_array(
        decoded_span,
        encoded_span,
        bits_per_entry,
        dense
    );
    return encoded_arr;
}


void init_long_array(py::module m_parent) {
    auto m = m_parent.def_submodule("long_array");

    m.def(
        "decode_long_array",
        [](
            py::buffer encoded_buffer,
            size_t size,
            std::uint8_t bits_per_entry,
            bool dense
        ) -> py::array {
            py::buffer_info encoded_buffer_info = encoded_buffer.request();
            // validate the input
            if (!(encoded_buffer_info.item_type_is_equivalent_to<std::int64_t>() || encoded_buffer_info.item_type_is_equivalent_to<std::uint64_t>())) {
                throw std::invalid_argument("dtype must be (u)int64.");
            }
            if (encoded_buffer_info.ndim != 1){
                throw std::invalid_argument("Only 1D arrays are supported.");
            }
            if (encoded_buffer_info.strides[0] != encoded_buffer_info.itemsize){
                throw std::invalid_argument("Slices are not supported.");
            }
            // Get the array as a span
            const std::span<std::uint64_t> encoded_span(
                static_cast<std::uint64_t*>(encoded_buffer_info.ptr),
                encoded_buffer_info.size
            );
            
            size_t byte_length = std::pow(2, std::ceil(std::log2(std::ceil(static_cast<float>(bits_per_entry) / 8))));
            switch (byte_length) {
            case 1:
                return _decode_long_array<std::uint8_t>(size, bits_per_entry, dense, encoded_span);
            case 2:
                return _decode_long_array<std::uint16_t>(size, bits_per_entry, dense, encoded_span);
            case 4:
                return _decode_long_array<std::uint32_t>(size, bits_per_entry, dense, encoded_span);
            case 8:
                return _decode_long_array<std::uint64_t>(size, bits_per_entry, dense, encoded_span);
            default:
                throw std::runtime_error("Byte length must be 1, 2, 4 or 8. Got " + std::to_string(byte_length));
            }
        },
        py::arg("long_array"),
        py::arg("size"),
        py::arg("bits_per_entry"),
        py::arg("dense") = true,
        py::doc(
            "Decode a long array (from BlockStates or Heightmaps)\n"
            "\n"
            ":param long_array: Encoded long array\n"
            ":param size: The expected size of the returned array\n"
            ":param bits_per_entry: The number of bits per entry in the encoded array.\n"
            ":param dense: If true the long arrays will be treated as a bit stream. If false they are distinct values with padding\n"
            ":return: Decoded array as numpy array"
        )
    );

    m.def(
        "encode_long_array",
        [](
            py::buffer decoded_buffer,
            std::variant<std::monostate, std::uint8_t> bits_per_entry,
            bool dense,
            std::uint8_t min_bits_per_entry_union
        ) -> py::array_t<std::uint64_t> {
            py::buffer_info decoded_buffer_info = decoded_buffer.request();
            // validate the input
            if (decoded_buffer_info.ndim != 1){
                throw std::invalid_argument("Only 1D arrays are supported.");
            }
            if (decoded_buffer_info.strides[0] != decoded_buffer_info.itemsize){
                throw std::invalid_argument("Slices are not supported.");
            }

            if (decoded_buffer_info.item_type_is_equivalent_to<std::uint64_t>()) {
                return _encode_long_array<std::uint64_t>(decoded_buffer_info, bits_per_entry, dense, min_bits_per_entry_union);
            }
            else if (decoded_buffer_info.item_type_is_equivalent_to<std::uint32_t>()) {
                return _encode_long_array<std::uint32_t>(decoded_buffer_info, bits_per_entry, dense, min_bits_per_entry_union);
            }
            else if (decoded_buffer_info.item_type_is_equivalent_to<std::uint16_t>()) {
                return _encode_long_array<std::uint16_t>(decoded_buffer_info, bits_per_entry, dense, min_bits_per_entry_union);
            }
            else if (decoded_buffer_info.item_type_is_equivalent_to<std::uint8_t>()) {
                return _encode_long_array<std::uint8_t>(decoded_buffer_info, bits_per_entry, dense, min_bits_per_entry_union);
            }
            else {
                throw std::invalid_argument("array must be an unsigned integer array in native byte order.");
            }
        },
        py::arg("array"),
        py::arg("bits_per_entry") = py::none(),
        py::arg("dense") = true,
        py::arg("min_bits_per_entry") = 1,
        py::doc(
            "Encode a long array (from BlockStates or Heightmaps)\n"
            "\n"
            ":param array: A numpy array of the data to be encoded.\n"
            ":param bits_per_entry: The number of bits to use to store each value. If left as None will use the smallest bits per entry.\n"
            ":param dense: If true the long arrays will be treated as a bit stream. If false they are distinct values with padding\n"
            ":param min_bits_per_entry: The mimimum value that bits_per_entry can be. If it is less than this it will be capped at this value.\n"
            ":return: Encoded array as numpy array"
        )
    );
}
