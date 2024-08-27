#include <memory>
#include <stdexcept>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>

#include "iterator.py.hpp"

namespace py = pybind11;

void init_collections_iterator(py::module m) {
	// A Python iterator class around an arbitrary C++ object.
	// This can only be constructed from C++.
	// This does not own the C++ object so the lifespan of this object must be
	// tied to the lifespan of the Python object that does own the C++ object.
	py::class_<
		Amulet::collections::Iterator,
		std::shared_ptr<Amulet::collections::Iterator>
	> Iterator(m, "Iterator");
	Iterator.def(
		"__next__",
		[](Amulet::collections::Iterator& self) {
			if (self.has_next()) {
				return self.next();
			}
			throw py::stop_iteration("");
		}
	);
	Iterator.def(
		"__iter__",
		[](std::shared_ptr<Amulet::collections::Iterator> self) {
			return self;
		}
	);
}
