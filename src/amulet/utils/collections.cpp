#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>

#include <amulet_py/collections_abc.hpp>

namespace py = pybind11;

PYBIND11_MODULE(collections, m) {
	py::class_<Amulet::collections_abc::PySequenceIterator>(m, "PySequenceIterator")
		.def(
			"__next__",
			[](Amulet::collections_abc::PySequenceIterator& self) {
				if (self.has_next()) {
					return self.next();
				}
				throw py::stop_iteration("");
			}
		)
		.def(
			"__iter__",
			[](Amulet::collections_abc::PySequenceIterator& self) {
				return self;
			}
			);
}
