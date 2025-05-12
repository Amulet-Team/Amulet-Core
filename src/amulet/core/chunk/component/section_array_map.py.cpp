#include <pybind11/numpy.h>
#include <pybind11/operators.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <limits>
#include <memory>
#include <span>
#include <variant>

#include <amulet/pybind11_extensions/numpy.hpp>

#include <amulet/pybind11_extensions/iterator.hpp>
#include <amulet/pybind11_extensions/mapping.hpp>
#include <amulet/pybind11_extensions/mutable_mapping.hpp>

#include "section_array_map.hpp"

namespace py = pybind11;
namespace pyext = Amulet::pybind11_extensions;

py::module init_section_array_map(py::module m_parent)
{
    auto m = m_parent.def_submodule("section_array_map");

    // 3D index array
    py::class_<Amulet::IndexArray3D, std::shared_ptr<Amulet::IndexArray3D>>
        IndexArray3D(m, "IndexArray3D", py::buffer_protocol(),
            "A 3D index array.");
    // Constructors
    IndexArray3D.def(
        py::init<const Amulet::SectionShape&>(),
        py::arg("shape"));
    IndexArray3D.def(
        py::init<
            const Amulet::SectionShape&,
            std::uint32_t>(),
        py::arg("shape"),
        py::arg("value"));
    IndexArray3D.def(
        py::init<const Amulet::IndexArray3D&>(),
        py::arg("other"));
    auto index_array_from_buffer = [](py::buffer other) {
        py::buffer_info info = other.request();
        if (!info.item_type_is_equivalent_to<std::uint32_t>()) {
            throw std::invalid_argument("Array must be a std::uint32_t array.");
        }
        if (info.ndim != 3) {
            throw std::invalid_argument("Array must have 3 dimensions.");
        }

        // Get the source array
        auto src = static_cast<std::uint32_t*>(info.ptr);

        // Get the shape
        size_t x_dim = info.shape[0];
        size_t y_dim = info.shape[1];
        size_t z_dim = info.shape[2];

        if (
            x_dim > std::numeric_limits<std::uint16_t>::max() || y_dim > std::numeric_limits<std::uint16_t>::max() || z_dim > std::numeric_limits<std::uint16_t>::max()) {
            throw std::invalid_argument("IndexArray3D has a maximum dimension of 65535.");
        }

        // Get the destination array
        auto self = std::make_shared<Amulet::IndexArray3D>(
            std::make_tuple(
                static_cast<std::uint16_t>(x_dim),
                static_cast<std::uint16_t>(y_dim),
                static_cast<std::uint16_t>(z_dim)));
        auto dst = self->get_buffer();

        // Get the source strides
        size_t x_src_stride = info.strides[0] / sizeof(std::uint32_t);
        size_t y_src_stride = info.strides[1] / sizeof(std::uint32_t);
        size_t z_src_stride = info.strides[2] / sizeof(std::uint32_t);

        // Get the destination strides
        size_t x_dst_stride = y_dim * z_dim;
        size_t y_dst_stride = y_dim;

        // copy the buffer
        for (size_t x = 0; x < x_dim; x++) {
            for (size_t y = 0; y < y_dim; y++) {
                for (size_t z = 0; z < z_dim; z++) {
                    std::uint32_t* src_ptr = src + x * x_src_stride + y * y_src_stride + z * z_src_stride;
                    std::uint32_t* dst_ptr = dst + x * x_dst_stride + y * y_dst_stride + z;
                    *(dst_ptr) = *(src_ptr);
                }
            }
        }
        return self;
    };
    IndexArray3D.def(
        py::init(index_array_from_buffer));
    IndexArray3D.def_property_readonly(
        "shape",
        &Amulet::IndexArray3D::get_shape);
    IndexArray3D.def_property_readonly(
        "size",
        &Amulet::IndexArray3D::get_size);
    IndexArray3D.def_buffer([](Amulet::IndexArray3D& self) {
        return py::buffer_info(
            self.get_buffer(),
            sizeof(std::uint32_t),
            py::format_descriptor<std::uint32_t>::format(),
            3,
            { std::get<0>(self.get_shape()),
                std::get<1>(self.get_shape()),
                std::get<2>(self.get_shape()) },
            { sizeof(std::uint32_t) * std::get<1>(self.get_shape()) * std::get<2>(self.get_shape()),
                sizeof(std::uint32_t) * std::get<2>(self.get_shape()),
                sizeof(std::uint32_t) });
    });

    // Section Array Map
    py::class_<Amulet::SectionArrayMap, std::shared_ptr<Amulet::SectionArrayMap>>
        SectionArrayMap(m, "SectionArrayMap",
            "A container of sub-chunk arrays.");
    SectionArrayMap.def(
        py::init(
            [&index_array_from_buffer](
                const Amulet::SectionShape& array_shape,
                std::variant<
                    std::uint32_t,
                    std::shared_ptr<Amulet::IndexArray3D>,
                    py::buffer>
                    default_array) {
                return std::visit([&array_shape, &index_array_from_buffer](auto&& arg) {
                    using T = std::decay_t<decltype(arg)>;
                    if constexpr (std::is_same_v<T, py::buffer>) {
                        return std::make_shared<Amulet::SectionArrayMap>(array_shape, index_array_from_buffer(arg));
                    } else {
                        return std::make_shared<Amulet::SectionArrayMap>(array_shape, arg);
                    }
                },
                    default_array);
            }),
        py::arg("array_shape"),
        py::arg("default_array"));
    SectionArrayMap.def_property_readonly(
        "array_shape",
        &Amulet::SectionArrayMap::get_array_shape);
    py::object asarray = py::module::import("numpy").attr("asarray");
    SectionArrayMap.def_property(
        "default_array",
        [asarray](const Amulet::SectionArrayMap& self) {
            return std::visit([asarray](auto&& arg) -> std::variant<std::uint32_t, py::array> {
                using T = std::decay_t<decltype(arg)>;
                if constexpr (std::is_same_v<T, std::uint32_t>) {
                    return arg;
                } else {
                    static_assert(std::is_same_v<T, std::shared_ptr<Amulet::IndexArray3D>>);
                    return asarray(py::cast(arg));
                }
            },
                self.get_default_array());
        },
        [&index_array_from_buffer](
            Amulet::SectionArrayMap& self,
            std::variant<
                std::uint32_t,
                std::shared_ptr<Amulet::IndexArray3D>,
                py::buffer>
                default_array) {
            std::visit([&self, &index_array_from_buffer](auto&& arg) {
                using T = std::decay_t<decltype(arg)>;
                if constexpr (
                    std::is_same_v<T, std::uint32_t> || std::is_same_v<T, std::shared_ptr<Amulet::IndexArray3D>>) {
                    self.set_default_array(arg);
                } else {
                    self.set_default_array(index_array_from_buffer(arg));
                }
            },
                default_array);
        });
    SectionArrayMap.def(
        "populate",
        &Amulet::SectionArrayMap::populate_section);
    SectionArrayMap.def(
        "__setitem__",
        [&index_array_from_buffer](
            Amulet::SectionArrayMap& self,
            std::int64_t cy,
            std::variant<
                std::shared_ptr<Amulet::IndexArray3D>,
                py::buffer>
                array_) {
            std::visit([&self, &index_array_from_buffer, &cy](auto&& arg) {
                using T = std::decay_t<decltype(arg)>;
                if constexpr (
                    std::is_same_v<T, std::shared_ptr<Amulet::IndexArray3D>>) {
                    self.set_section(cy, arg);
                } else {
                    self.set_section(cy, index_array_from_buffer(arg));
                }
            },
                array_);
        });
    SectionArrayMap.def(
        "__delitem__",
        &Amulet::SectionArrayMap::del_section);
    SectionArrayMap.def(
        "__getitem__",
        [asarray](const Amulet::SectionArrayMap& self, std::int64_t cy) -> pyext::numpy::array_t<std::uint32_t> {
            try {
                return asarray(py::cast(self.get_section(cy)));
            } catch (const std::out_of_range&) {
                throw py::key_error(std::to_string(cy));
            }
        });
    SectionArrayMap.def(
        "__len__",
        &Amulet::SectionArrayMap::get_size);
    SectionArrayMap.def(
        "__iter__",
        [](const Amulet::SectionArrayMap& self) -> pyext::collections::Iterator<std::int64_t> {
            return pyext::make_iterator(pyext::detail::MapIterator(self.get_arrays()));
        },
        py::keep_alive<0, 1>());
    SectionArrayMap.def(
        "__contains__",
        &Amulet::SectionArrayMap::contains_section);
    pyext::collections::def_Mapping_keys<std::int64_t>(SectionArrayMap);
    pyext::collections::def_Mapping_values<pyext::numpy::array_t<std::uint32_t>>(SectionArrayMap);
    pyext::collections::def_Mapping_items<std::int64_t, pyext::numpy::array_t<std::uint32_t>>(SectionArrayMap);
    pyext::collections::def_Mapping_get<std::int64_t, pyext::numpy::array_t<std::uint32_t>>(SectionArrayMap);
    pyext::collections::def_Mapping_eq(SectionArrayMap);
    pyext::collections::def_Mapping_hash(SectionArrayMap);
    pyext::collections::def_MutableMapping_pop<std::int64_t, pyext::numpy::array_t<std::uint32_t>>(SectionArrayMap);
    pyext::collections::def_MutableMapping_popitem<std::int64_t, pyext::numpy::array_t<std::uint32_t>>(SectionArrayMap);
    pyext::collections::def_MutableMapping_update(SectionArrayMap);
    pyext::collections::def_MutableMapping_setdefault<std::int64_t, pyext::numpy::array_t<std::uint32_t>>(SectionArrayMap);
    pyext::collections::register_MutableMapping(SectionArrayMap);

    return m;
}
