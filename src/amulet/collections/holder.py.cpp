#include <pybind11/pybind11.h>

#include "holder.py.hpp"

namespace py = pybind11;

void init_collections_holder(py::module m) {
	py::class_<Amulet::collections::Holder> Holder(m, "Holder",
		"A utility class for keeping smart pointers alive."
	);
}
