#include <pybind11/pybind11.h>
namespace py = pybind11;

void init_utils_collections(py::module);
void init_utils_numpy(py::module);

void init_utils(py::module utils_module){
    auto utils_numpy_module = utils_module.def_submodule("numpy");
    init_utils_numpy(utils_numpy_module);
}
