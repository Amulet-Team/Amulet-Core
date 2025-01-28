#include <pybind11/pybind11.h>

#include <pybind11_extensions/py_module.hpp>

namespace py = pybind11;

void init_collections_holder(py::module);
void init_collections_iterator(py::module);
void init_collections_mapping(py::module);
void init_collections_mutable_mapping(py::module);

void init_collections(py::module m_parent)
{
    auto m = pybind11_extensions::def_subpackage(m_parent, "collections");
    init_collections_holder(m);
    init_collections_iterator(m);
    init_collections_mapping(m);
    init_collections_mutable_mapping(m);
}
