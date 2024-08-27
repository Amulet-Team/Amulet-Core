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
	py::object KeysView = py::module::import("collections.abc").attr("KeysView");
	Mapping.def(
		"keys",
		[KeysView](Amulet::collections::Mapping& self) {
			return KeysView(py::cast(self));
		}
	);
	py::object ValuesView = py::module::import("collections.abc").attr("ValuesView");
	Mapping.def(
		"values",
		[ValuesView](Amulet::collections::Mapping& self) {
			return ValuesView(py::cast(self));
		}
	);
	py::object ItemsView = py::module::import("collections.abc").attr("ItemsView");
	Mapping.def(
		"items",
		[ItemsView](Amulet::collections::Mapping& self) {
			return ItemsView(py::cast(self));
		}
	);
}
