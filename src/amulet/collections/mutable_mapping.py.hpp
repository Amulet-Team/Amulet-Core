#pragma once

#include <memory>

#include <pybind11/pybind11.h>

#include "mapping.py.hpp"

namespace py = pybind11;

namespace Amulet {
namespace collections {
	template <typename clsT>
	void PyMutableMapping_pop(clsT cls) {
		py::object marker = py::module::import("builtins").attr("Ellipsis");
		cls.def(
			"pop",
			[marker](py::object self, py::object key, py::object default_) {
				py::object value;
				try {
					value = self.attr("__getitem__")(key);
				}
				catch (const py::error_already_set& e) {
					if (e.matches(PyExc_KeyError)) {
						if (default_.is(marker)) {
							throw;
						}
						return default_;
					}
					else {
						throw;
					}
				}
				self.attr("__delitem__")(key);
				return value;
			},
			py::arg("key"),
			py::arg("default") = marker
		);
	}

	template <typename clsT>
	void PyMutableMapping_popitem(clsT cls) {
		py::object iter = py::module::import("builtins").attr("iter");
		py::object next = py::module::import("builtins").attr("next");
		cls.def(
			"popitem",
			[iter, next](py::object self) {
				py::object key;
				try {
					key = next(iter(self));
				} 
				catch (const py::error_already_set& e) {
					if (e.matches(PyExc_StopIteration)) {
						throw py::key_error();
					}
					else {
						throw;
					}
				}
				py::object value = self.attr("__getitem__")(key);
				self.attr("__delitem__")(key);
				return std::make_pair(key, value);
			}
		);
	}

	template <typename clsT>
	void PyMutableMapping_clear(clsT cls) {
		cls.def(
			"clear",
			[](py::object self) {
				try {
					while (true) {
						self.attr("popitem")();
					}
				}
				catch (const py::error_already_set& e) {
					if (!e.matches(PyExc_KeyError)) {
						throw;
					}
				}
			}
		);
	}

	template <typename clsT>
	void PyMutableMapping_update(clsT cls) {
		py::object isinstance = py::module::import("builtins").attr("isinstance");
		py::object hasattr = py::module::import("builtins").attr("hasattr");
		py::object PyMapping = py::module::import("collections.abc").attr("Mapping");
		cls.def(
			"update",
			[
				isinstance, 
				hasattr, 
				PyMapping
			](
				py::object self, 
				py::object other, 
				py::kwargs kwargs
			) {
				if (isinstance(other, PyMapping)) {
					for (auto it = other.begin(); it != other.end(); it++) {
						self.attr("__setitem__")(*it, other.attr("__getitem__")(*it));
					}
				}
				else if (hasattr(other, "keys")) {
					py::object keys = other.attr("keys")();
					for (auto it = keys.begin(); it != keys.end(); it++) {
						self.attr("__setitem__")(*it, other.attr("__getitem__")(*it));
					}
				}
				else {
					for (auto it = other.begin(); it != other.end(); it++) {
						self.attr("__setitem__")(
							*it->attr("__getitem__")(0),
							*it->attr("__getitem__")(1)
						);
					}
				}
				py::object items = kwargs.attr("items")();
				for (auto it = items.begin(); it != items.end(); it++) {
					self.attr("__setitem__")(
						*it->attr("__getitem__")(0),
						*it->attr("__getitem__")(1)
					);
				}

			},
			py::arg("other") = py::tuple()
		);
	}

	template <typename clsT>
	void PyMutableMapping_setdefault(clsT cls) {
		cls.def(
			"setdefault",
			[](py::object self, py::object key, py::object default_ = py::none()) {
				try {
					return self.attr("__getitem__")(key);
				}
				catch (const py::error_already_set& e) {
					if (e.matches(PyExc_KeyError)) {
						self.attr("__setitem__")(key, default_);
					}
					else {
						throw;
					}
				}
				return default_;
			}
		);
	}

	template <typename clsT>
	void PyMutableMapping_register(clsT cls) {
		py::module::import("collections.abc").attr("MutableMapping").attr("register")(cls);
	}

	class MutableMapping : public Mapping {
	public:
		virtual ~MutableMapping() {};
		virtual void setitem(py::object py_key, py::object py_value) = 0;
		virtual void delitem(py::object py_key) = 0;
		virtual void clear() = 0;
	};

	template <typename mapT>
	class Map : public MutableMapping {
	private:
		py::object _owner;
		mapT& _map;
	public:
		Map(
			mapT& map,
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
		void setitem(py::object py_key, py::object py_value) override {
			_map.insert_or_assign(
				py_key.cast<typename mapT::key_type>(),
				py_value.cast<typename mapT::mapped_type>()
			);
		}
		void delitem(py::object py_key) override {
			_map.erase(py_key.cast<typename mapT::key_type>());
		}
		void clear() override {
			_map.clear();
		}
	};

	template <typename mapT>
	static py::object make_map(mapT& value, py::object owner = py::none()) {
		return py::cast(
			static_cast<std::shared_ptr<MutableMapping>>(
				std::make_shared<Map<mapT>>(value, owner)
			)
		);
	}
}
}
