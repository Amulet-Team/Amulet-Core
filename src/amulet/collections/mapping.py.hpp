#pragma once

#include <memory>

#include <pybind11/pybind11.h>

#include <amulet/pybind11/types.hpp>
#include "iterator.py.hpp"

namespace py = pybind11;

namespace Amulet {
namespace collections {
	template <typename clsT>
	void PyMapping_repr(clsT cls) {
		cls.def(
			"__repr__",
			[](py::object self) {
				std::string repr = "{";
				bool is_first = true;
				for (auto it = self.begin(); it != self.end(); it++) {
					if (is_first) {
						is_first = false;
					}
					else {
						repr += ", ";
					}
					repr += py::repr(*it);
					repr += ": ";
					repr += py::repr(self.attr("__getitem__")(*it));
				}
				repr += "}";
				return repr;
			}
		);
	}

	template <typename clsT>
	void PyMapping_contains(clsT cls) {
		cls.def(
			"__contains__",
			[](py::object self, py::object key) {  
				try {
					self.attr("__getitem__")(key);
					return true;
				}
				catch (const py::error_already_set& e) {
					if (e.matches(PyExc_KeyError)) {
						return false;
					}
					else {
						throw;
					}
				}
			}
		);
	}

	template <typename clsT>
	void PyMapping_keys(clsT cls) {
		py::object KeysView = py::module::import("collections.abc").attr("KeysView");
		cls.def(
			"keys",
			[KeysView](py::object self) { return KeysView(self); }
		);
	}

	template <typename clsT>
	void PyMapping_values(clsT cls) {
		py::object ValuesView = py::module::import("collections.abc").attr("ValuesView");
		cls.def(
			"values",
			[ValuesView](py::object self) { return ValuesView(self); }
		);
	}

	template <typename clsT>
	void PyMapping_items(clsT cls) {
		py::object ItemsView = py::module::import("collections.abc").attr("ItemsView");
		cls.def(
			"items",
			[ItemsView](py::object self) { return ItemsView(self); }
		);
	}

	template <typename clsT>
	void PyMapping_get(clsT cls) {
		cls.def(
			"get",
			[](py::object self, py::object key, py::object default_ = py::none()) {
				try {
					return self.attr("__getitem__")(key);
				}
				catch (const py::error_already_set& e) {
					if (e.matches(PyExc_KeyError)) {
						return default_;
					}
					else {
						throw;
					}
				}
			}
		);
	}

	template <typename clsT>
	void PyMapping_eq(clsT cls) {
		py::object dict = py::module::import("builtins").attr("dict");
		py::object isinstance = py::module::import("builtins").attr("isinstance");
		py::object NotImplemented = py::module::import("builtins").attr("NotImplemented");
		py::object PyMapping = py::module::import("collections.abc").attr("Mapping");
		cls.def(
			"__eq__",
			[
				dict,
				isinstance, 
				NotImplemented,
				PyMapping
			](
				py::object self, 
				py::object other
			) -> std::variant<bool, py::types::NotImplementedType> {
				if (!isinstance(other, PyMapping)) {
					return NotImplemented;
				}
				return dict(self.attr("items")()).equal(dict(other.attr("items")()).cast<py::dict>());
			}
		);
	}

	template <typename clsT>
	void PyMapping_hash(clsT cls) {
		cls.def(
			"__hash__",
			[](
				py::object self
			) -> size_t {
				throw py::type_error("Mapping is not hashable");
			}
		);
	}

	template <typename clsT>
	void PyMapping_register(clsT cls) {
		py::module::import("collections.abc").attr("Mapping").attr("register")(cls);
	}

	class Mapping {
	public:
		virtual ~Mapping() {};
		virtual py::object getitem(py::object py_key) const = 0;
		virtual std::shared_ptr<Iterator> iter() const = 0;
		virtual size_t size() const = 0;
		virtual bool contains(py::object py_key) const = 0;
	};

	template <typename mapT>
	class ConstMap : public Mapping {
	private:
		py::object _owner;
		const mapT& _map;
	public:
		ConstMap(
			const mapT& map,
			py::object owner = py::none()
		) : _owner(owner), _map(map) {}

		py::object getitem(py::object py_key) const override {
			return py::cast(_map.at(py_key.cast<typename mapT::key_type>()));
		}
		std::shared_ptr<Iterator> iter() const override {
			return std::make_shared<MapIterator<mapT>>(_map, _owner);
		}
		size_t size() const override {
			return _map.size();
		}
		bool contains(py::object py_key) const override {
			return _map.contains(py_key.cast<typename mapT::key_type>());
		}
	};

	template <typename mapT>
	static py::object make_const_map(const mapT& value, py::object owner = py::none()) {
		return py::cast(
			static_cast<std::shared_ptr<Mapping>>(
				std::make_shared<ConstMap<mapT>>(value, owner)
			)
		);
	}

}
}
