#pragma once

#include <algorithm>
#include <cstddef>
#include <memory>

#include <pybind11/pybind11.h>
#include "iterator.py.hpp"
#include <amulet/pybind11/collections.hpp>
#include <amulet/pybind11/python.hpp>

namespace py = pybind11;

namespace Amulet {
	namespace collections {

		template <typename clsT>
		void Sequence_getitem_slice(clsT cls) {
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

		template <typename clsT>
		void Sequence_contains(clsT cls) {
			cls.def(
				"__contains__",
				[](py::object self, py::object value) {
					py::iterator it = py::iter(self);
					while (it != py::iterator::sentinel()) {
						if (py::equals(*it, value)) {
							return true;
						}
						++it;
					}
					return false;
				}
			);
		}

		template <typename elemT = py::object, typename clsT>
		void Sequence_iter(clsT cls) {
			cls.def(
				"__iter__",
				[](py::object self) -> py::collections::Iterator<elemT> {
					return py::cast(
						static_cast<std::shared_ptr<Amulet::collections::Iterator>>(
							std::make_shared<PySequenceIterator>(self, 0, 1)
						)
					);
				}
			);
		}

		template <typename elemT = py::object, typename clsT>
		void Sequence_reversed(clsT cls) {
			cls.def(
				"__reversed__",
				[](py::object self) -> py::collections::Iterator<elemT> {
					return py::cast(
						static_cast<std::shared_ptr<Amulet::collections::Iterator>>(
							std::make_shared<PySequenceIterator>(self, py::len(self) - 1, -1)
						)
					);
				}
			);
		}

		template <typename clsT>
		void Sequence_index(clsT cls) {
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

						if (py::equals(value, obj)) {
							return start;
						}

						start++;
					}
					throw py::value_error("");
				},
				py::arg("value"), py::arg("start") = 0, py::arg("stop") = std::numeric_limits<Py_ssize_t>::max()
					);
		}

		template <typename clsT>
		void Sequence_count(clsT cls) {
			cls.def(
				"count",
				[](py::object self, py::object value) {
					size_t count = 0;
					size_t size = py::len(self);
					py::object getitem = self.attr("__getitem__");
					for (size_t i = 0; i < size; ++i) {
						if (py::equals(value, getitem(i))) {
							count++;
						}
					}
					return count;
				},
				py::arg("value")
					);
		}

		template <typename clsT>
		void Sequence_register(clsT cls) {
			py::module::import("collections.abc").attr("Sequence").attr("register")(cls);
		}

		template <typename elemT = py::object, typename clsT>
		void Sequence(clsT cls) {
			Sequence_getitem_slice(cls);
			Sequence_contains(cls);
			Sequence_iter<elemT>(cls);
			Sequence_reversed<elemT>(cls);
			Sequence_index(cls);
			Sequence_count(cls);
			Sequence_register(cls);
		}
	}
}
