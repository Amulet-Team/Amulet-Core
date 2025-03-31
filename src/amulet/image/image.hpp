#pragma once

#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>

#include <filesystem>
#include <string>
#include <string_view>

#include <amulet/dll.hpp>

namespace py = pybind11;

namespace PIL {
namespace Image {

    // Is the object an image.
    // The GIL must be held when calling this.
    AMULET_CORE_EXPORT bool is_image(py::handle obj);

    // A C++ wrapper around a Pillow Image class.
    // The GIL must be held while interacting with this class.
    class Image : public py::object {
    public:
        PYBIND11_OBJECT_DEFAULT(Image, py::object, is_image)

        // Get the image width.
        // The GIL must be held while calling this.
        AMULET_CORE_EXPORT size_t get_width() const;

        // Get the image height.
        // The GIL must be held while calling this.
        AMULET_CORE_EXPORT size_t get_height() const;

        // Get the image mode.
        // The GIL must be held while calling this.
        AMULET_CORE_EXPORT std::string get_mode() const;

        // Get the image buffer.
        // The GIL must be held before calling and while interacting with the buffer.
        AMULET_CORE_EXPORT py::buffer get_buffer() const;
    };

    // Open an image file at the given path.
    // The GIL must be held while calling this and while interacting with the image.
    AMULET_CORE_EXPORT Image open(const std::filesystem::path& path);

    // Load an image file from its raw data.
    // The GIL must be held while calling this and while interacting with the image.
    AMULET_CORE_EXPORT Image load(std::string_view data);

} // namespace Image
} // namespace PIL

namespace pybind11 {
namespace detail {

    template <>
    struct handle_type_name<PIL::Image::Image> {
        static constexpr auto name = const_name("PIL.Image.Image");
    };

} // namespace detail
} // namespace pybind11

namespace Amulet {

AMULET_CORE_EXPORT PIL::Image::Image get_missing_no_icon();
AMULET_CORE_EXPORT PIL::Image::Image get_missing_pack_icon();
AMULET_CORE_EXPORT PIL::Image::Image get_missing_world_icon();

} // namespace Amulet
