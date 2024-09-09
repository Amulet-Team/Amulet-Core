#pragma once

#include <pybind11/pybind11.h>

namespace py = pybind11;

namespace pybind11 {
	inline bool equals(
	    py::object l,
	    py::object r
	){
		py::object l_result = l.attr("__eq__")(r);
		py::object NotImplemented = py::module::import("builtins").attr("NotImplemented");
		if (l_result.is(NotImplemented)){
		    py::object r_result = r.attr("__eq__")(l);
		    if (r_result.is(NotImplemented)){
                return false;
            } else {
                return r_result.cast<bool>();
            }
		} else {
		    return l_result.cast<bool>();
		}
	}
}
