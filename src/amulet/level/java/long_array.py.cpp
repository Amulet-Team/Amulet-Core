#include <span>
#include <cmath>
#include <string>

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

#include "long_array.hpp"

namespace py = pybind11;


template <typename dstT>
py::array_t<dstT> _decode_long_array(
    size_t size,
    std::uint8_t bits_per_entry,
    bool dense,
    const std::span<std::uint64_t>& src_span
) {
    // create the dst array
    py::array_t<dstT> dst_arr(size);
    py::buffer_info inverse_info = dst_arr.request();
    // Get the dst array as a span
    std::span<dstT> dst_span(
        static_cast<dstT*>(inverse_info.ptr),
        inverse_info.size
    );
    Amulet::decode_long_array(
        src_span,
        dst_span,
        bits_per_entry,
        dense
    );
    return dst_arr;
};


void init_long_array(py::module m_parent) {
    auto m = m_parent.def_submodule("long_array");

    m.def(
        "decode_long_array",
        [](
            py::buffer src_buffer,
            size_t size,
            std::uint8_t bits_per_entry,
            bool dense
        ) -> py::array {
            py::buffer_info src_buffer_info = src_buffer.request();
            // validate the input
            if (!(src_buffer_info.item_type_is_equivalent_to<std::int64_t>() || src_buffer_info.item_type_is_equivalent_to<std::uint64_t>())) {
                throw std::invalid_argument("dtype must be (u)int64.");
            }
            if (src_buffer_info.ndim != 1){
                throw std::invalid_argument("Only 1D arrays are supported.");
            }
            if (src_buffer_info.strides[0] != src_buffer_info.itemsize){
                throw std::invalid_argument("Slices are not supported.");
            }
            // Get the array as a span
            const std::span<std::uint64_t> src_span(
                static_cast<std::uint64_t*>(src_buffer_info.ptr),
                src_buffer_info.size
            );
            
            size_t byte_length = std::pow(2, std::ceil(std::log2(std::ceil(static_cast<float>(bits_per_entry) / 8))));
            switch (byte_length) {
            case 1:
                return _decode_long_array<std::uint8_t>(size, bits_per_entry, dense, src_span);
            case 2:
                return _decode_long_array<std::uint16_t>(size, bits_per_entry, dense, src_span);
            case 4:
                return _decode_long_array<std::uint32_t>(size, bits_per_entry, dense, src_span);
            case 8:
                return _decode_long_array<std::uint64_t>(size, bits_per_entry, dense, src_span);
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
}
