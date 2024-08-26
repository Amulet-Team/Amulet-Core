#include <memory>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>

#include <amulet/utils/collections.py.hpp>

namespace py = pybind11;

void init_utils_collections(py::module m) {
	py::options options;

	py::class_<Amulet::collections_abc::PySequenceIterator> PySequenceIterator(m, "PySequenceIterator");
		PySequenceIterator.def(
			"__next__",
			[](Amulet::collections_abc::PySequenceIterator& self) {
				if (self.has_next()) {
					return self.next();
				}
				throw py::stop_iteration("");
			}
		);
		PySequenceIterator.def(
			"__iter__",
			[](Amulet::collections_abc::PySequenceIterator& self) {
				return self;
			}
		);
}
