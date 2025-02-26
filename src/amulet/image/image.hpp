#pragma once

#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>

#include <filesystem>
#include <string>
#include <string_view>

#include <amulet/dll.hpp>

namespace py = pybind11;

inline bool is_image(py::handle obj)
{
    py::gil_scoped_acquire gil;
    auto ImageCls = py::module::import("PIL.Image").attr("Image");
    return py::module::import("builtins").attr("isinstance")(obj, ImageCls).cast<bool>();
}

namespace PIL {
namespace Image {

    // A C++ wrapper around a Pillow Image class.
    class Image : public py::object {
    public:
        PYBIND11_OBJECT_DEFAULT(Image, py::object, is_image)

        size_t get_width()
        {
            return attr("width").cast<size_t>();
        }

        size_t get_height()
        {
            return attr("height").cast<size_t>();
        }

        std::string get_mode()
        {
            return attr("mode").cast<std::string>();
        }

        py::buffer get_buffer()
        {
            return *this;
        }
    };

    inline Image open(std::filesystem::path path)
    {
        return py::module::import("PIL.Image").attr("open")(path.string());
    }

    inline Image load(std::string_view data)
    {
        py::bytes py_data(data);
        auto f = py::module::import("io").attr("BytesIO")(py_data);
        return py::module::import("PIL.Image").attr("open")(f);
    }

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
