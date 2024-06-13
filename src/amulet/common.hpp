#pragma once
#define PYBIND11_DETAILED_ERROR_MESSAGES

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/operators.h>
#include <pybind11/numpy.h>


#define PYCOMMON(type)\
    type.def("__repr__", &Amulet::type::repr);\
    type.def(py::pickle(&Amulet::type::serialise, &Amulet::type::deserialise));
