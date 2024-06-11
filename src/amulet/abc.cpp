#include "abc.hpp"
#include <amuletcpp/abc.hpp>


namespace py = pybind11;

PYBIND11_MODULE(abc, m) {
    py::class_<Amulet::ABC, std::shared_ptr<Amulet::ABC>> ABC(m, "ABC");
        ABC.def(
            "__repr__",
            &Amulet::ABC::repr);
}
