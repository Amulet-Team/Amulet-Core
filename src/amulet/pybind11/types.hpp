#pragma once
#include <pybind11/pybind11.h>

namespace pybind11 {
	namespace types {
		class NotImplementedType : public object {
			PYBIND11_OBJECT_DEFAULT(NotImplementedType, object, PyObject_Type)
				using object::object;
		};
	}
	namespace detail {
		template <>
		struct handle_type_name<types::NotImplementedType> {
			static constexpr auto name = const_name("types.NotImplementedType");
		};
	}
}
