#pragma once

#include <pybind11/pybind11.h>

namespace py = pybind11;


template <typename clsT>
void hash_default(clsT cls) {
    cls.def(
        "__hash__",
        [](py::object self) -> py::int_ {
            return py::module::import("builtins").attr("id")(self);
        }
    );
}


template <typename clsT>
void hash_disable(clsT cls) {
    cls.def(
        "__hash__",
        [](py::object self) -> size_t {
            throw py::type_error("This class is not hashable.");
        }
    );
}
