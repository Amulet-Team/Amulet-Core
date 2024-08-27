// This is a C++ implementation of the python collections.abc module
// These functions will add the minxin methods and register your class with the ABC.

#pragma once
#include <stdexcept>

#include <pybind11/pybind11.h>

namespace py = pybind11;

namespace Amulet {
namespace collections {
	class Iterator {
	public:
		virtual ~Iterator() {};
		virtual bool has_next() = 0;
		virtual py::object next() = 0;
	};

	template <typename mapT>
	class MapIterator: public Iterator {
	private:
		py::object owner;
		const mapT& map;
		mapT::const_iterator begin;
		mapT::const_iterator end;
		mapT::const_iterator pos;
		size_t size;

	public:
		MapIterator(const mapT& map, py::object owner = py::none()) :
			owner(owner),
			map(map),
			begin(map.begin()),
			end(map.end()),
			pos(map.begin()),
			size(map.size())
		{}

		bool has_next() override {
			return pos != end;
		}

		bool is_valid() {
			// This is not fool proof.
			// There are cases where this is true but the iterator is invalid.
			// The programmer should write good code and this will catch some of the bad cases.
			return size == map.size() && begin == map.begin() && end == map.end();
		}

		py::object next() override {
			if (!is_valid()) {
				throw std::runtime_error("map changed size during iteration.");
			}
			return py::cast((pos++)->first);
		}
	};

}
}
