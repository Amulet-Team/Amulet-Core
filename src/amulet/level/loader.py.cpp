#include <pybind11/pybind11.h>
#include <pybind11_extensions/py_module.hpp>

#include "loader.hpp"

namespace py = pybind11;

py::module init_level_loader(py::module m_parent)
{
    auto m = m_parent.def_submodule("loader");

    py::register_exception<Amulet::NoValidLevelLoader>(m, "NoValidLevelLoader");

    py::class_<Amulet::LevelLoaderToken> LevelLoaderToken(m, "LevelLoaderToken");
    LevelLoaderToken.def("repr", &Amulet::LevelLoaderToken::repr);
    LevelLoaderToken.def("__hash__", &Amulet::LevelLoaderToken::hash);
    LevelLoaderToken.def("__eq__", &Amulet::LevelLoaderToken::operator==);

    py::class_<Amulet::LevelLoaderPathToken> LevelLoaderPathToken(m, "LevelLoaderPathToken");
    LevelLoaderPathToken.def(py::init<std::filesystem::path>());

    m.def("get_level", &Amulet::get_level, py::arg("token"));
    
    return m;
}
