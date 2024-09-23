#pragma once
#include <pybind11/pybind11.h>
#include <pybind11/detail/descr.h>
#include <vector>

namespace py = pybind11;

namespace Amulet {
	namespace pybind11 {
		namespace detail {
			template<size_t N>
			struct FixedString {
				char buf[N + 1]{};
				constexpr FixedString(char const* s) {
					for (unsigned i = 0; i != N; ++i) buf[i] = s[i];
				}
			};
			template<unsigned N>
			FixedString(char const (&)[N])->FixedString<N - 1>;
		}

		// Type hint for a native python object.
		namespace type_hints {
			template <detail::FixedString T>
			class PyObjectStr : public py::object {
				PYBIND11_OBJECT_DEFAULT(PyObjectStr, object, PyObject_Type)
					using object::object;
			};

			template <typename cppT>
			class PyObjectCpp : public py::object {
				PYBIND11_OBJECT_DEFAULT(PyObjectCpp, object, PyObject_Type)
					using object::object;
			};
		}
	}
}

namespace pybind11 {
	namespace detail {
		template <Amulet::pybind11::detail::FixedString T>
		struct handle_type_name<Amulet::pybind11::type_hints::PyObjectStr<T>> {
			static constexpr auto name = pybind11::detail::const_name(T.buf);
		};

		template <typename cppT>
		struct handle_type_name<Amulet::pybind11::type_hints::PyObjectCpp<cppT>> {
			static constexpr auto name = make_caster<cppT>::name;
		};
	}
}
