#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>

#include <amulet/utils/numpy/unique.hpp>

namespace py = pybind11;

PYBIND11_MODULE(numpy, m) {
    m.def("unique_inverse", [](py::buffer arr_buffer){
        py::buffer_info arr_info = arr_buffer.request();
        // validate the input
        if (!(
            arr_info.format == py::format_descriptor<std::uint32_t>::format() ||
            (arr_info.format == "L" && arr_info.itemsize == 4)
        )) {
            throw std::invalid_argument("dtype must be uint32.");
        }
        if (arr_info.ndim != 1){
            throw std::invalid_argument("Only 1D arrays are supported.");
        }
        if (arr_info.strides[0] != arr_info.itemsize){
            throw std::invalid_argument("Slices are not supported.");
        }
        // Get the array as a span
        const std::span<std::uint32_t> arr(
            static_cast<std::uint32_t*>(arr_info.ptr),
            arr_info.size
        );
        // create the unique container
        std::vector<std::uint32_t> unique;
        // create the inverse array
        py::array_t<std::uint32_t> inverse_arr(arr_info.shape);
        py::buffer_info inverse_info = inverse_arr.request();
        // Get the inverse array as a span
        std::span<std::uint32_t> inverse(
            static_cast<std::uint32_t*>(inverse_info.ptr),
            inverse_info.size
        );
        // Call unique
        Amulet::unique_inverse(arr, unique, inverse);
        // create the unique array
        py::array_t<std::uint32_t> unique_arr(unique.size(), unique.data());
        // Return the new values
        return std::pair(unique_arr, inverse_arr);
    });
}
