#include <memory>
#include <span>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/operators.h>

#include <amulet/utils/collections.py.hpp>
#include <amulet/chunk_components/section_array_map.hpp>

#include <iostream>


namespace py = pybind11;

void init_section_array_map(py::module section_array_map_module) {
    // 3D index array
    py::class_<Amulet::IndexArray3D, std::shared_ptr<Amulet::IndexArray3D>>
        IndexArray3D(section_array_map_module, "IndexArray3D", py::buffer_protocol(),
            "A 3D index array."
        );
    // Constructors
    IndexArray3D.def(
        py::init<const Amulet::SectionShape&>(),
        py::arg("shape")
    );
    IndexArray3D.def(
        py::init<
            const Amulet::SectionShape&,
            std::uint32_t
        >(),
        py::arg("shape"),
        py::arg("value")
    );
    IndexArray3D.def(
        py::init<const Amulet::IndexArray3D&>(),
        py::arg("other")
    );
    IndexArray3D.def(
        py::init(
            [](py::buffer other) {
                py::buffer_info info = other.request();
                if (!(
                    (sizeof(unsigned int) == 4 && info.format != "I") || 
                    (sizeof(unsigned long) == 4 && info.format != "L")
                )) {
                    throw std::runtime_error("Array must be a std::uint32_t array.");
                }
                if (info.ndim != 3) {
                    throw std::runtime_error("Array must have 3 dimensions.");
                }

                // Get the source array
                auto src = static_cast<std::uint32_t*>(info.ptr);

                // Get the shape
                size_t x_dim = info.shape[0];
                size_t y_dim = info.shape[1];
                size_t z_dim = info.shape[2];

                // Get the destination array
                auto self = std::make_shared<Amulet::IndexArray3D>(std::make_tuple(x_dim, y_dim, z_dim));
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
            }
        )
    );
    IndexArray3D.def_property_readonly(
        "shape",
        &Amulet::IndexArray3D::get_shape
    );
    IndexArray3D.def_property_readonly(
        "size",
        &Amulet::IndexArray3D::get_size
    );
    IndexArray3D.def_buffer([](Amulet::IndexArray3D& self) {
        return py::buffer_info(
            self.get_buffer(),
            sizeof(std::uint32_t),
            py::format_descriptor<std::uint32_t>::format(),
            3,
            {
                std::get<0>(self.get_shape()),
                std::get<1>(self.get_shape()),
                std::get<2>(self.get_shape())
            },
            {
                sizeof(std::uint32_t) * std::get<1>(self.get_shape()) * std::get<2>(self.get_shape()),
                sizeof(std::uint32_t) * std::get<2>(self.get_shape()),
                sizeof(std::uint32_t)
            }
        );
    });
    
}
