#pragma once
#include <pybind11/pybind11.h>

namespace pybind11 {
	namespace collections {
		template <typename T>
		class Iterator : public object {
			PYBIND11_OBJECT_DEFAULT(Iterator, object, PyObject_Type)
				using object::object;
		};
	}
	namespace detail {
		template <typename T>
		struct handle_type_name<collections::Iterator<T>> {
			static constexpr auto name =
				const_name("collections.abc.Iterator[") +
				make_caster<T>::name +
				const_name("]");
		};
	}
	
	namespace collections {
		template <typename T>
		class Sequence : public object {
			PYBIND11_OBJECT_DEFAULT(Sequence, object, PyObject_Type)
				using object::object;
		};
	}
	namespace detail {
		template <typename T>
		struct handle_type_name<collections::Sequence<T>> {
			static constexpr auto name =
				const_name("collections.abc.Sequence[") +
				make_caster<T>::name +
				const_name("]");
		};
	}
	
	namespace collections {
		template <typename K, typename V>
		class Mapping : public object {
			PYBIND11_OBJECT_DEFAULT(Mapping, object, PyObject_Type)
				using object::object;
		};
	}
	namespace detail {
		template <typename K, typename V>
		struct handle_type_name<collections::Mapping<K, V>> {
			static constexpr auto name =
				const_name("collections.abc.Mapping[") +
				make_caster<K>::name +
				const_name(", ") +
				make_caster<V>::name +
				const_name("]");
		};
	}

	namespace collections {
		template <typename K, typename V>
		class MutableMapping : public object {
			PYBIND11_OBJECT_DEFAULT(MutableMapping, object, PyObject_Type)
			using object::object;
		};
	}
	namespace detail {
		template <typename K, typename V>
		struct handle_type_name<collections::MutableMapping<K, V>> {
			static constexpr auto name =
				const_name("collections.abc.MutableMapping[") +
				make_caster<K>::name +
				const_name(", ")
				+ make_caster<V>::name +
				const_name("]");
		};
	}
}
