#include <pybind11/pybind11.h>
namespace py = pybind11;


void init_java_chunk_encode(py::module m_parent) {
	auto m = m_parent.def_submodule("_chunk_encode");
}
