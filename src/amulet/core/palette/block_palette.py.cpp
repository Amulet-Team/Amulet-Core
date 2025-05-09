#include <pybind11/operators.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <memory>
#include <sstream>
#include <string>
#include <variant>

#include <amulet/pybind11_extensions/sequence.hpp>

#include <amulet/core/block/block.hpp>

#include "block_palette.hpp"

namespace py = pybind11;
namespace pyext = Amulet::pybind11_extensions;

inline void bounds_check(const size_t& size, Py_ssize_t& index)
{
    if (index < 0) {
        index += size;
        if (index < 0) {
            throw py::index_error();
        }
    } else if (index >= size) {
        throw py::index_error();
    }
}

void init_block_palette(py::module block_palette_module)
{
    py::object PyList = py::module::import("builtins").attr("list");
    py::class_<Amulet::BlockPalette, std::shared_ptr<Amulet::BlockPalette>, Amulet::VersionRangeContainer> BlockPalette(block_palette_module, "BlockPalette");
    BlockPalette.def(
        py::init<const Amulet::VersionRange&>());
    BlockPalette.def(
        "__repr__",
        [PyList](const Amulet::BlockPalette& self) {
            return "BlockPalette(" + py::repr(py::cast(self.get_version_range())).cast<std::string>() + ") # " + py::repr(PyList(py::cast(self))).cast<std::string>();
        });
    BlockPalette.def(
        "__len__",
        &Amulet::BlockPalette::size);
    BlockPalette.def(
        "__getitem__",
        [](Amulet::BlockPalette& self, Py_ssize_t index) {
            bounds_check(self.size(), index);
            return self.index_to_block_stack(index);
        });
    pyext::collections::def_Sequence_getitem_slice(BlockPalette);
    BlockPalette.def(
        "__contains__",
        [](const Amulet::BlockPalette& self, Py_ssize_t index) {
            return index < self.size();
        });
    BlockPalette.def(
        "__contains__",
        &Amulet::BlockPalette::contains_block);
    pyext::collections::def_Sequence_iter<Amulet::BlockStack>(BlockPalette);
    pyext::collections::def_Sequence_reversed<Amulet::BlockStack>(BlockPalette);
    pyext::collections::def_Sequence_index(BlockPalette);
    pyext::collections::def_Sequence_count(BlockPalette);
    pyext::collections::register_Sequence(BlockPalette);

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
            ":raises IndexError if there is no block stack at that index."));

    BlockPalette.def(
        "block_stack_to_index",
        &Amulet::BlockPalette::block_stack_to_index,
        py::doc(
            "Get the index of the block stack in the palette.\n"
            "If it is not in the palette already it will be added first.\n"
            "\n"
            ":param block_stack: The block stack to get the index of.\n"
            ":return: The index of the block stack in the palette."));
}
