#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/typing.h>

#include <iostream>

#include "signal.hpp"

namespace py = pybind11;

namespace Amulet {

template <typename... Args>
class PySignal : public py::object {
    PYBIND11_OBJECT_DEFAULT(PySignal, object, PyObject_Type)
    using object::object;
};

template <typename... Args>
PySignal<Args...> make_signal(Signal<Args...>& signal)
{
    if (!pybind11::detail::get_type_info(typeid(Signal<Args...>), false)) {
        pybind11::class_<SignalToken<Args...>>(pybind11::handle(), "SignalToken", pybind11::module_local());

        pybind11::class_<Signal<Args...>>(pybind11::handle(), "Signal", pybind11::module_local())
            .def("connect", &Signal<Args...>::connect)
            .def("disconnect", &Signal<Args...>::disconnect)
            .def("emit", &Signal<Args...>::emit);
    }
    return pybind11::cast(signal, py::return_value_policy::reference);
}

};

namespace pybind11 {
namespace detail {
    template <typename T, typename... Ts>
    constexpr auto get_signal_type_hint()
    {
        if constexpr ((sizeof...(Ts)) == 0) {
            return const_name("amulet.utils.signal.Signal[") + make_caster<T>::name + const_name("]");
        } else {
            return const_name("amulet.utils.signal.Signal[") + make_caster<T>::name + ((const_name(", ") + make_caster<Ts>::name) + ...) + const_name("]");
        }
    }

    template <>
    struct handle_type_name<Amulet::PySignal<>> {
        static constexpr auto name = const_name("amulet.utils.signal.Signal[()]");
    };

    template <typename T, typename... Ts>
    struct handle_type_name<Amulet::PySignal<T, Ts...>> {
        static constexpr auto name = get_signal_type_hint<T, Ts...>();
    };
}
}
