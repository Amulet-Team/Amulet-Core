#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "mutable_mapping.py.hpp"

namespace py = pybind11;

void init_collections_mutable_mapping(py::module m) {
	py::class_<
		Amulet::collections::MutableMapping,
		std::shared_ptr<Amulet::collections::MutableMapping>,
		Amulet::collections::Mapping
	> MutableMapping(m, "MutableMapping");
	MutableMapping.def(
		"__setitem__",
		&Amulet::collections::MutableMapping::setitem
	);
	MutableMapping.def(
		"__delitem__",
		&Amulet::collections::MutableMapping::delitem
	);
}
