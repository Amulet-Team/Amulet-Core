#include <sstream>
#include <string>
#include <memory>
#include <variant>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/operators.h>

#include <amulet/biome.hpp>
#include <amulet/palette/biome_palette.hpp>
#include <amulet/collections/sequence.py.hpp>

namespace py = pybind11;

inline void bounds_check(const size_t& size, Py_ssize_t& index) {
	if (index < 0) {
		index += size;
		if (index < 0) {
			throw py::index_error();
		}
	}
	else if (index >= size) {
		throw py::index_error();
	}
}

void init_biome_palette(py::module biome_palette_module) {
    py::object PyList = py::module::import("builtins").attr("list");
	py::class_<Amulet::BiomePalette, std::shared_ptr<Amulet::BiomePalette>, Amulet::VersionRangeContainer> BiomePalette(biome_palette_module, "BiomePalette");
		BiomePalette.def(
			py::init<std::shared_ptr<Amulet::VersionRange>>()
		);
		BiomePalette.def(
			"__repr__",
			[PyList](const Amulet::BiomePalette& self) {
				return "BiomePalette(" +
                    py::repr(py::cast(self.get_version_range())).cast<std::string>() + 
				") # " +
                    py::repr(PyList(py::cast(self))).cast<std::string>();
			}
		);
		BiomePalette.def(
			"__len__",
			&Amulet::BiomePalette::size
		);
		BiomePalette.def(
			"__getitem__",
			[](Amulet::BiomePalette& self, Py_ssize_t index) {
				bounds_check(self.size(), index);
				return self.index_to_biome(index);
			}
		);
		Amulet::collections::Sequence_getitem_slice(BiomePalette);
		//Amulet::collections::Sequence_contains(BiomePalette);
		BiomePalette.def(
			"__contains__",
			[](const Amulet::BiomePalette& self, Py_ssize_t index) {
				return index < self.size();
			}
		);
		BiomePalette.def(
			"__contains__",
			[](const Amulet::BiomePalette& self, std::shared_ptr<Amulet::Biome> item) {
				return self.contains_biome(item);
			}
		);
		Amulet::collections::Sequence_iter(BiomePalette);
		Amulet::collections::Sequence_reversed(BiomePalette);
		Amulet::collections::Sequence_index(BiomePalette);
		Amulet::collections::Sequence_count(BiomePalette);
		Amulet::collections::Sequence_register(BiomePalette);

		BiomePalette.def(
			"index_to_biome",
			[](Amulet::BiomePalette& self, Py_ssize_t index) {
				bounds_check(self.size(), index);
				return self.index_to_biome(index);
			},
			py::doc(
				"Get the biome at the specified palette index.\n"
				"\n"
				":param index: The index to get\n"
				":return: The biome at that index\n"
				":raises IndexError if there is no biome at that index."
			)
		);

		BiomePalette.def(
			"biome_to_index",
			[](Amulet::BiomePalette& self, std::shared_ptr<Amulet::Biome> item) {
				return self.biome_to_index(item);
			},
			py::doc(
				"Get the index of the biome in the palette.\n"
				"If it is not in the palette already it will be added first.\n"
				"\n"
				":param biome: The biome to get the index of.\n"
				":return: The index of the biome in the palette."
			)
		);
}
