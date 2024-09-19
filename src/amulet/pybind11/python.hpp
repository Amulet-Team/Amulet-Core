#pragma once

#include <pybind11/pybind11.h>

namespace py = pybind11;

namespace pybind11 {
	inline bool equals(
	    const py::handle l,
	    const py::handle r
	){
		return PyObject_RichCompare(l.ptr(), r.ptr(), Py_EQ);
	}
}
