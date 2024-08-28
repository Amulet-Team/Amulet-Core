#pragma once
// Better type hinting for equality methods that pybind11 has natively

#include <variant>
#include <amulet/pybind11/types.hpp>

#include <pybind11/pybind11.h>

namespace py = pybind11;

template <typename R, typename clsT>
void Eq(clsT cls) {
    cls.def(
        "__eq__",
        [](const clsT::type& self, R other) {
            return self == other;
        }
    );
    cls.def(
        "__ne__",
        [](const clsT::type& self, R other) {
            return self != other;
        }
    );
}


template <typename clsT>
void Eq(clsT cls) {
    Eq<const clsT::type&>(cls);
}


template <typename clsT>
void Eq_default(clsT cls) {
    py::object NotImplemented = py::module::import("builtins").attr("NotImplemented");
    cls.def(
        "__eq__",
        [NotImplemented](const clsT::type& self, py::object other) -> std::variant<bool, py::types::NotImplementedType> {
            return NotImplemented;
        }
    );
    cls.def(
        "__ne__",
        [NotImplemented](const clsT::type& self, py::object other) -> std::variant<bool, py::types::NotImplementedType> {
            return NotImplemented;
        }
    );
}
