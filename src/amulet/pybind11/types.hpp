#pragma once
#include <pybind11/pybind11.h>

namespace py = pybind11;

namespace Amulet {
	namespace pybind11 {
		namespace types {
			class NotImplementedType : public py::object {
				PYBIND11_OBJECT_DEFAULT(NotImplementedType, object, PyObject_Type)
				using object::object;
			};
		}
		
	}
}

namespace pybind11 {
	namespace detail {
		template <>
		struct handle_type_name<Amulet::pybind11::types::NotImplementedType> {
			static constexpr auto name = const_name("types.NotImplementedType");
		};
	}
}
