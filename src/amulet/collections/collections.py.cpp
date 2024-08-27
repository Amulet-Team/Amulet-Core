#include <memory>
#include <stdexcept>

#include <pybind11/pybind11.h>

#include "collections.py.hpp"

namespace py = pybind11;

void init_collections_holder(py::module);
void init_collections_iterator(py::module);
void init_collections_mapping(py::module);
void init_collections_mutable_mapping(py::module);

void init_collections(py::module m) {
	init_collections_holder(m);
	init_collections_iterator(m);
	init_collections_mapping(m);
	init_collections_mutable_mapping(m);

	py::class_<Amulet::collections::PySequenceIterator> PySequenceIterator(m, "PySequenceIterator");
		PySequenceIterator.def(
			"__next__",
			[](Amulet::collections::PySequenceIterator& self) {
				if (self.has_next()) {
					return self.next();
				}
				throw py::stop_iteration("");
			}
		);
		PySequenceIterator.def(
			"__iter__",
			[](Amulet::collections::PySequenceIterator& self) {
				return self;
			}
		);
}
