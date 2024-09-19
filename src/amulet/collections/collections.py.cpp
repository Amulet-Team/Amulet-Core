#include <memory>
#include <stdexcept>

#include <pybind11/pybind11.h>

namespace py = pybind11;

void init_collections_holder(py::module);
void init_collections_iterator(py::module);
void init_collections_mapping(py::module);
void init_collections_mutable_mapping(py::module);

void init_collections(py::module m_parent) {
	auto m = m_parent.def_submodule("collections");
	init_collections_holder(m);
	init_collections_iterator(m);
	init_collections_mapping(m);
	init_collections_mutable_mapping(m);
}
