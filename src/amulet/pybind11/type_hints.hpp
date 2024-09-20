#pragma once
#include <pybind11/pybind11.h>
#include <vector>

namespace Amulet {
	namespace pybind11 {
		namespace detail {
			template<size_t N>
			struct FixedString {
				static constexpr unsigned size = N;
				char buf[N + 1]{};
				constexpr FixedString(char const* s) {
					for (unsigned i = 0; i != N; ++i) buf[i] = s[i];
				}
				constexpr pybind11::detail::descr<N> descr() const { return pybind11::detail::descr<N>(buf); }
			};
			template<unsigned N>
			FixedString(char const (&)[N])->FixedString<N - 1>;
		}

		// Type hint for a native python object.
		namespace type_hints {
			template <detail::FixedString T>
			class PyObject : public object {
				PYBIND11_OBJECT_DEFAULT(PyObject, object, PyObject_Type)
					using object::object;
			};
		}
	}
}

namespace pybind11 {
	namespace detail {
		template <Amulet::pybind11::detail::FixedString T>
		struct handle_type_name<Amulet::pybind11::type_hints::PyObject<T>> {
			static constexpr auto name = T.descr();
		};
	}
}
