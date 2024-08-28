#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "mapping.py.hpp"

namespace py = pybind11;

void init_collections_mapping(py::module m) {
	py::class_<
		Amulet::collections::Mapping,
		std::shared_ptr<Amulet::collections::Mapping>
	> Mapping(m, "Mapping");
	Mapping.def(
		"__getitem__",
		[](Amulet::collections::Mapping& self, py::object key) {
			try {
				return self.getitem(key);
			}
			catch (const std::out_of_range&) {
				throw py::key_error(py::repr(key));
			}
		}
	);
	Mapping.def(
		"__iter__",
		&Amulet::collections::Mapping::iter
	);
	Mapping.def(
		"__len__",
		&Amulet::collections::Mapping::size
	);
	Mapping.def(
		"__contains__",
		&Amulet::collections::Mapping::contains
	);
	Amulet::collections::PyMapping_repr(Mapping);
	Amulet::collections::PyMapping_keys(Mapping);
	Amulet::collections::PyMapping_values(Mapping);
	Amulet::collections::PyMapping_items(Mapping);
	Amulet::collections::PyMapping_get(Mapping);
	Amulet::collections::PyMapping_eq(Mapping);
	Amulet::collections::PyMapping_register(Mapping);
}
