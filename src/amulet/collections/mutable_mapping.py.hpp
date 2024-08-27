#pragma once

#include <memory>

#include <pybind11/pybind11.h>

#include "mapping.py.hpp"

namespace py = pybind11;

namespace Amulet {
namespace collections {
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
		void setitem(py::object py_key, py::object py_value) override {
			_map.insert_or_assign(
				py_key.cast<mapT::key_type>(),
				py_value.cast<mapT::mapped_type>()
			);
		}
		void delitem(py::object py_key) override {
			_map.erase(py_key.cast<mapT::key_type>());
		}
		void clear() override {
			_map.clear();
		}
	};
}
}
