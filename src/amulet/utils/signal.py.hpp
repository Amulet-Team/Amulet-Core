#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/typing.h>

#include <iostream>

#include "signal.hpp"
#include <amulet/utils/holder.py.hpp>

namespace py = pybind11;

namespace Amulet {

template <typename... Args>
class PySignal : public py::object {
    PYBIND11_OBJECT_DEFAULT(PySignal, object, PyObject_Type)
    using object::object;
};

template <typename... Args>
class PySignalToken : public py::object {
    PYBIND11_OBJECT_DEFAULT(PySignalToken, object, PyObject_Type)
    using object::object;
};

// Create a python binding for the signal class.
template <typename signalT>
void create_signal_binding()
{
    if (!pybind11::detail::get_type_info(typeid(signalT), false)) {
        pybind11::class_<typename signalT::tokenT>(pybind11::handle(), "SignalToken", pybind11::module_local());

        pybind11::class_<signalT, Amulet::nogil_shared_ptr<signalT>>(pybind11::handle(), "Signal", pybind11::module_local())
            .def("connect", &signalT::connect, py::call_guard<py::gil_scoped_release>())
            .def("disconnect", &signalT::disconnect, py::call_guard<py::gil_scoped_release>())
            .def("emit", &signalT::emit, py::call_guard<py::gil_scoped_release>())
            .def("emit_async", &signalT::emit_async, py::call_guard<py::gil_scoped_release>());
    }
}

// Define a signal getter on a class.
// This automatically creates the binding class.
template <typename PyCls, typename CppCls, typename... Args>
void def_signal(PyCls& cls, const char* name, const Signal<Args...> CppCls::*attr)
{
    create_signal_binding<Signal<Args...>>();
    cls.def_property_readonly(
        name,
        [attr](const typename PyCls::type& self) -> PySignal<Args...> {
            return pybind11::cast(self.*attr, py::return_value_policy::reference);
        });
}

};

namespace pybind11 {
namespace detail {
    namespace {

        template <typename T, typename... Ts>
        constexpr auto get_args_str()
        {
            if constexpr ((sizeof...(Ts)) == 0) {
                return make_caster<T>::name;
            } else {
                return make_caster<T>::name + ((const_name(", ") + make_caster<Ts>::name) + ...);
            }
        }

    }

    template <>
    struct handle_type_name<Amulet::PySignal<>> {
        static constexpr auto name = const_name("amulet.utils.signal.Signal[()]");
    };

    template <typename T, typename... Ts>
    struct handle_type_name<Amulet::PySignal<T, Ts...>> {
        static constexpr auto name = const_name("amulet.utils.signal.Signal[") + get_args_str<T, Ts...>() + const_name("]");
    };

    template <>
    struct handle_type_name<Amulet::PySignalToken<>> {
        static constexpr auto name = const_name("amulet.utils.signal.SignalToken[()]");
    };

    template <typename T, typename... Ts>
    struct handle_type_name<Amulet::PySignalToken<T, Ts...>> {
        static constexpr auto name = const_name("amulet.utils.signal.SignalToken[") + get_args_str<T, Ts...>() + const_name("]");
    };
}
}
