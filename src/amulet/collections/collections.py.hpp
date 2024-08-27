// This is a C++ implementation of the python collections.abc module
// These functions will add the minxin methods and register your class with the ABC.

#pragma once

#include <algorithm>
#include <cstddef>
#include <memory>

#include <pybind11/pybind11.h>

namespace py = pybind11;

namespace Amulet {
namespace collections {

	template <typename T>
	void Sequence_getitem_slice(T cls) {
		cls.def(
			"__getitem__",
			[](py::object self, const py::slice& slice) {
				size_t start = 0, stop = 0, step = 0, slicelength = 0;
				if (!slice.compute(py::len(self), &start, &stop, &step, &slicelength)) {
					throw py::error_already_set();
				}
				py::list out(slicelength);
				py::object getitem = self.attr("__getitem__");
				for (size_t i = 0; i < slicelength; ++i) {
					out[i] = getitem(start);
					start += step;
				}
				return out;
			}
		);
	}
	
	template <typename T>
	void Sequence_contains(T cls) {
		cls.def(
			"__contains__",
			[](py::object self, py::object value) {
				py::iterator it = py::iter(self);
				while (it != py::iterator::sentinel()) {
					if (*it == value) {
						return true;
					}
					++it;
				}
				return false;
			}
		);
	}

	class PySequenceIterator {
		private:
			py::object obj;
			size_t index;
			std::ptrdiff_t step;
		public:
			PySequenceIterator(
				py::object obj,
				size_t index,
				std::ptrdiff_t step
			) : obj(obj), index(index), step(step) {};
			py::object next() {
				py::object item = obj.attr("__getitem__")(index);
				index += step;
				return item;
			};
			bool has_next() { return 0 <= index && index < py::len(obj); };
	};

	inline void _register_sequence_iterator() {
		py::module::import("amulet.collections");
	}

	template <typename T>
	void Sequence_iter(T cls) {
		_register_sequence_iterator();
		cls.def(
			"__iter__",
			[](py::object self) {
				return PySequenceIterator(self, 0, 1);
			}
		);
	}

	template <typename T>
	void Sequence_reversed(T cls) {
		_register_sequence_iterator();
		cls.def(
			"__reversed__",
			[](py::object self) {
				return PySequenceIterator(self, py::len(self), -1);
			}
		);
	}

	template <typename T>
	void Sequence_index(T cls) {
		cls.def(
			"index",
			[](py::object self, py::object value, Py_ssize_t s_start, Py_ssize_t s_stop) {
				size_t size = py::len(self);
				size_t start;
				size_t stop;
				if (s_start < 0) {
					start = std::max<Py_ssize_t>(0, size + s_start);
				}
				else {
					start = s_start;
				}
				if (s_stop < 0) {
					stop = size + s_stop;
				}
				else {
					stop = s_stop;
				}
				py::object getitem = self.attr("__getitem__");
				while (start < stop) {
					py::object obj;
					try {
						obj = getitem(start);
					}
					catch (py::error_already_set& e) {
						if (e.matches(PyExc_IndexError)) {
							break;
						}
						else {
							throw;
						}
					}

					if (value == obj) {
						return start;
					}
					
					start++;
				}
				throw py::value_error("");
			},
			py::arg("value"), py::arg("start") = 0, py::arg("stop") = std::numeric_limits<Py_ssize_t>::max()
		);
	}

	template <typename T>
	void Sequence_count(T cls) {
		cls.def(
			"count",
			[](py::object self, py::object value) {
				size_t count = 0;
				size_t size = py::len(self);
				py::object getitem = self.attr("__getitem__");
				for (size_t i = 0; i < size; ++i) {
					if (value == getitem(i)) {
						count++;
					}
				}
				return count;
			},
			py::arg("value")
		);
	}

	template <typename T>
	void Sequence_register(T cls) {
		py::module::import("collections.abc").attr("Sequence").attr("register")(cls);
	}

	template <typename T>
	void Sequence(T cls) {
		Sequence_getitem_slice(cls);
		Sequence_contains(cls);
		Sequence_iter(cls);
		Sequence_reversed(cls);
		Sequence_index(cls);
		Sequence_count(cls);
		Sequence_register(cls);
	}
}
}
