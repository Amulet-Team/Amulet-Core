#pragma once
#include <pybind11/pybind11.h>

namespace py = pybind11;

namespace Amulet {
	namespace pybind11 {
		namespace collections {
			template <typename T>
			class Iterator : public py::object {
				PYBIND11_OBJECT_DEFAULT(Iterator, object, PyObject_Type)
				using object::object;
			};
		}

		namespace collections {
			template <typename T>
			class Sequence : public py::object {
				PYBIND11_OBJECT_DEFAULT(Sequence, object, PyObject_Type)
				using object::object;
			};
		}

		namespace collections {
			template <typename K, typename V>
			class Mapping : public py::object {
				PYBIND11_OBJECT_DEFAULT(Mapping, object, PyObject_Type)
				using object::object;
			};
		}

		namespace collections {
			template <typename K, typename V>
			class MutableMapping : public py::object {
				PYBIND11_OBJECT_DEFAULT(MutableMapping, object, PyObject_Type)
				using object::object;
			};
		}
	}
}

namespace pybind11 {
	namespace detail {
		template <typename T>
		struct handle_type_name<Amulet::pybind11::collections::Iterator<T>> {
			static constexpr auto name =
				const_name("collections.abc.Iterator[") +
				make_caster<T>::name +
				const_name("]");
		};

		template <typename T>
		struct handle_type_name<Amulet::pybind11::collections::Sequence<T>> {
			static constexpr auto name =
				const_name("collections.abc.Sequence[") +
				make_caster<T>::name +
				const_name("]");
		};

		template <typename K, typename V>
		struct handle_type_name<Amulet::pybind11::collections::Mapping<K, V>> {
			static constexpr auto name =
				const_name("collections.abc.Mapping[") +
				make_caster<K>::name +
				const_name(", ") +
				make_caster<V>::name +
				const_name("]");
		};

		template <typename K, typename V>
		struct handle_type_name<Amulet::pybind11::collections::MutableMapping<K, V>> {
			static constexpr auto name =
				const_name("collections.abc.MutableMapping[") +
				make_caster<K>::name +
				const_name(", ")
				+ make_caster<V>::name +
				const_name("]");
		};
	}
}
