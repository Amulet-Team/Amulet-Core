#pragma once

#include <string>
#include <functional>
#include <filesystem>
#include <map>
#include <utility>

#include <pybind11/pybind11.h>
#include <amulet/pybind11/typing.hpp>

namespace py = pybind11;

namespace pybind11 {
	inline void def_package_path(py::module m_parent, py::module m, std::string name) {
		py::list paths;
		py::list parent_paths = m_parent.attr("__path__").cast<py::list>();
		for (auto py_path : parent_paths) {
			if (py::isinstance<py::str>(py_path)) {
				std::string path = py_path.cast<std::string>();
				path.push_back(std::filesystem::path::preferred_separator);
				path.append(name);
				paths.append(py::cast(path));
			}
		}
		m.attr("__path__") = paths;
	}

	inline module def_subpackage(py::module m_parent, std::string name) {
		auto m = m_parent.def_submodule(name.c_str());
		def_package_path(m_parent, m, name);
		return m;
	}
}
