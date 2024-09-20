#pragma once
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

namespace py = pybind11;

namespace Amulet {
	namespace pybind11 {
		namespace numpy {
			template <typename T, int ExtraFlags = py::array::forcecast>
			class array_t : public py::array_t<T, ExtraFlags> {
				using py::array_t<T, ExtraFlags>::array_t;
			};
		}
	}
}

namespace pybind11 {
	namespace detail {
		template <typename T, int Flags>
		struct handle_type_name<Amulet::pybind11::numpy::array_t<T, Flags>> {
			static constexpr auto name
				= const_name("numpy.typing.NDArray[") + npy_format_descriptor<T>::name + const_name("]");
		};
	}
}
