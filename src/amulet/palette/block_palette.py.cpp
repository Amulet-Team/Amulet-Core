#include <sstream>
#include <string>
#include <memory>
#include <variant>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/operators.h>

#include <amulet/block.hpp>
#include <amulet/palette/block_palette.hpp>
#include <amulet/utils/collections.py.hpp>

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

void init_block_palette(py::module block_palette_module) {
	py::object PyList = py::module::import("builtins").attr("list");
	py::object VersionRangeContainer = py::module::import("amulet.version").attr("VersionRangeContainer");
	py::module::import("amulet.block");
	py::class_<Amulet::BlockPalette, std::shared_ptr<Amulet::BlockPalette>> BlockPalette(block_palette_module, "BlockPalette", VersionRangeContainer);
		BlockPalette.def(
			py::init<std::shared_ptr<Amulet::VersionRange>>()
		);
		BlockPalette.def(
			"__repr__",
			[PyList](const Amulet::BlockPalette& self) {
				return "BlockPalette(" +
                    py::repr(py::cast(self.get_version_range())).cast<std::string>() + 
				") # " +
                    py::repr(PyList(py::cast(self))).cast<std::string>();
			}
		);
		BlockPalette.def(
			"__len__",
			&Amulet::BlockPalette::size
		);
		BlockPalette.def(
			"__getitem__",
			[](Amulet::BlockPalette& self, Py_ssize_t index) {
				bounds_check(self.size(), index);
				return self.index_to_block_stack(index);
			}
		);
		Amulet::collections_abc::Sequence_getitem_slice(BlockPalette);
		//Amulet::collections_abc::Sequence_contains(BlockPalette);
		BlockPalette.def(
			"__contains__",
			[](const Amulet::BlockPalette& self, Py_ssize_t index) {
				return index < self.size();
			}
		);
		BlockPalette.def(
			"__contains__",
			[](const Amulet::BlockPalette& self, std::shared_ptr<Amulet::BlockStack> item) {
				return self.contains_block(item);
			}
		);
		Amulet::collections_abc::Sequence_iter(BlockPalette);
		Amulet::collections_abc::Sequence_reversed(BlockPalette);
		Amulet::collections_abc::Sequence_index(BlockPalette);
		Amulet::collections_abc::Sequence_count(BlockPalette);
		Amulet::collections_abc::Sequence_register(BlockPalette);

		BlockPalette.def(
			"index_to_block_stack",
			[](Amulet::BlockPalette& self, Py_ssize_t index) {
				bounds_check(self.size(), index);
				return self.index_to_block_stack(index);
			},
			py::doc(
				"Get the block stack at the specified palette index.\n"
				"\n"
				":param index: The index to get\n"
				":return: The block stack at that index\n"
				":raises IndexError if there is no block stack at that index."
			)
		);

		BlockPalette.def(
			"block_stack_to_index",
			[](Amulet::BlockPalette& self, std::shared_ptr<Amulet::BlockStack> item) {
				return self.block_stack_to_index(item);
			},
			py::doc(
				"Get the index of the block stack in the palette.\n"
				"If it is not in the palette already it will be added first.\n"
				"\n"
				":param block_stack: The block stack to get the index of.\n"
				":return: The index of the block stack in the palette."
			)
		);
}
