#include <pybind11/pybind11.h>

namespace pybind11 {
	namespace collections {
		template <typename K, typename V>
		class Mapping : public object {
			PYBIND11_OBJECT_DEFAULT(Mapping, object, PyObject_Type)
			using object::object;
		};
		template <typename K, typename V>
		class MutableMapping : public object {
			PYBIND11_OBJECT_DEFAULT(MutableMapping, object, PyObject_Type)
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
