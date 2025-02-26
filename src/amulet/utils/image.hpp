#pragma once

#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>

#include <filesystem>
#include <string>

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

} // namespace Image

} // namespace PIL

namespace PYBIND11_NAMESPACE {
namespace detail {
    template <>
    struct type_caster<PIL::Image::Image> {
    public:
        PYBIND11_TYPE_CASTER(PIL::Image::Image, const_name("PIL.Image.Image"));

        // Python->C++
        bool load(handle src, bool)
        {
            if (!is_image(src)) {
                return false;
            }
            value.ptr() = src.ptr();
            return true;
        }

        // C++ -> Python
        static handle cast(PIL::Image::Image src, return_value_policy /* policy */, handle /* parent */)
        {
            return src;
        }
    };
}
} // namespace PYBIND11_NAMESPACE::detail
