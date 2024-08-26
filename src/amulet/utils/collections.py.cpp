#include <memory>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>

#include <amulet/utils/collections.py.hpp>

namespace py = pybind11;

void init_utils_collections(py::module m) {
	py::options options;

	py::module::import("collections.abc");
	m.attr("_T") = py::module::import("typing").attr("TypeVar")(py::str("T"));

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
		options.disable_function_signatures();
		PySequenceIterator.attr("__class_getitem__") = PyClassMethod_New(
			py::cpp_function(
				[](const py::type& cls, const py::args& args) {return cls; },
				"__class_getitem__(cls, arg: type[_T]) -> collections.abc.Iterator[_T]"
			).ptr()
		);
		options.enable_function_signatures();

	// A Python iterator class around an arbitrary C++ object.
	// This can only be constructed from C++.
	// This does not own the C++ object so the lifespan of this object must be
	// tied to the lifespan of the Python object that does own the C++ object.
	py::class_<
		Amulet::collections_abc::PyIterator,
		std::shared_ptr<Amulet::collections_abc::PyIterator>
	> PyIterator(m, "PyIterator");
	PyIterator.def(
		"__next__",
		[](Amulet::collections_abc::PyIterator& self) {
			if (self.has_next()) {
				return self.next();
			}
			throw py::stop_iteration("");
		}
	);
	PyIterator.def(
		"__iter__",
		[](std::shared_ptr<Amulet::collections_abc::PyIterator> self) {
			return self;
		}
	);
	options.disable_function_signatures();
	PyIterator.attr("__class_getitem__") = PyClassMethod_New(
		py::cpp_function(
			[](const py::type& cls, const py::args& args) {return cls; },
			"__class_getitem__(cls, arg: type[_T]) -> collections.abc.Iterator[_T]"
		).ptr()
	);
	options.enable_function_signatures();
}
