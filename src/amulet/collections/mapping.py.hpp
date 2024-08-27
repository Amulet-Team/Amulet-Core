// This is a C++ implementation of the python collections.abc module
// These functions will add the minxin methods and register your class with the ABC.

#pragma once

#include <memory>

#include <pybind11/pybind11.h>

#include "iterator.py.hpp"

namespace py = pybind11;

namespace Amulet {
namespace collections {
	class Mapping {
	public:
		virtual ~Mapping() {};
		virtual py::object getitem(py::object py_key) const = 0;
		virtual std::unique_ptr<Iterator> iter() const = 0;
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
			py::object owner
		) : _owner(owner), _map(map) {}

		py::object getitem(py::object py_key) const override {
			return py::cast(_map.at(py_key.cast<mapT::key_type>()));
		}
		std::unique_ptr<Iterator> iter() const override {
			return std::make_unique<MapIterator<mapT>>(_map, _owner);
		}
		size_t size() const override {
			return _map.size();
		}
		bool contains(py::object py_key) const override {
			return _map.contains(py_key.cast<mapT::key_type>());
		}
	};

}
}
