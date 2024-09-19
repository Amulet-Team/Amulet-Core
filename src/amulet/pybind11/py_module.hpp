#pragma once

#include <string>
#include <functional>
#include <filesystem>
#include <map>
#include <utility>

#include <pybind11/pybind11.h>

namespace py = pybind11;

namespace pybind11 {
	// Define deferred variables
	inline void def_deferred(
		py::module m,
		std::map<std::string, std::function<py::object()>> attrs
	){
		m.def(
			"__getattr__",
			[attrs](py::object attr) -> py::object {
				if (py::isinstance<py::str>(attr)) {
					std::string attr_str = attr.cast<std::string>();
					auto it = attrs.find(attr_str);
					if (it != attrs.end()) {
						return it->second();
					}
				}
				throw py::attribute_error(py::repr(attr));
			}
		);
		m.def(
			"__dir__",
			[attrs, m]() {
				py::set names;
				// Add the variables defined in the module
				py::object dict = m.attr("__dict__");
				for (auto it = dict.begin(); it != dict.end(); it++) {
					names.add(*it);
				}
				// Add the deferred variables
				for (const auto& [name, _] : attrs) {
					names.add(py::str(name));
				}
				// Return as list
				return py::module::import("builtins").attr("list")(names);
			}
		);
	}

	inline std::pair<std::string, std::function<py::object()>> deferred_package_path(py::module m_parent, py::module m, std::string name) {
		auto getter = [m_parent, m, name]() {
			std::string path = m_parent.attr("__path__").attr("__getitem__")(0).cast<std::string>();
			path.push_back(std::filesystem::path::preferred_separator);
			path.append(name);
			py::list __path__;
			__path__.append(py::cast(path));
			return __path__;
		};
		return std::make_pair("__path__", getter);
	}

	inline std::pair<std::string, std::function<py::object()>> deferred_import(std::string module_name, std::string name) {
		auto getter = [module_name, name]() {
			return py::module::import(module_name.c_str()).attr(name.c_str());
		};
		return std::make_pair(name, getter);
	}
}
