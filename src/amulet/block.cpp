#include <span>

#include <amulet/block.hpp>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/operators.h>
#include <pybind11/typing.h>
#include <collections_abc.hpp>


namespace py = pybind11;

PYBIND11_MODULE(block, m) {
    py::options options;

    py::object PlatformVersionContainer = py::module::import("amulet.version").attr("PlatformVersionContainer");
    // Required for docstrings
    py::module::import("amulet_nbt");

    //py::object PyTuple = py::module::import("builtins").attr("tuple");
    py::object PySorted = py::module::import("builtins").attr("sorted");

    py::class_<Amulet::Block> Block(m, "Block", PlatformVersionContainer,
        "A class to manage the state of a block.\n"
        "\n"
        "It is an immutable object that contains the platform, version, namespace, base name and properties.\n"
        "\n"
        "Here's a few examples on how create a Block object:\n"
        "\n"
        ">>> # Create a stone block for Java 1.20.2\n"
        ">>> stone = Block(\"java\", VersionNumber(3578), \"minecraft\", \"stone\")\n"
        ">>> # The Java block version number is the Java data version\n"
        "\n"
        ">>> # Create a stone block for Bedrock \n"
        ">>> stone = Block(\"bedrock\", VersionNumber(1, 21, 0, 3), \"minecraft\", \"stone\")\n"
        ">>> # The Bedrock block version number is the value stored as an int with the block data.\n"
        "\n"
        ">>> # Create a Java water block with the level property\n"
        ">>> water = Block(\n"
        ">>>     \"java\", VersionNumber(3578),\n"
        ">>>     \"minecraft\",  # the namespace\n"
        ">>>     \"water\",  # the base name\n"
        ">>>     {  # A dictionary of properties.\n"
        ">>>         # Keys must be strings and values must be a numerical or string NBT type.\n"
        ">>>         \"level\": StringTag(\"0\")  # define a property `level` with a string value `0`\n"
        ">>>     }\n"
        ">>> )"
    );
        Block.def(
            py::init<
                const Amulet::PlatformType&,
                const Amulet::VersionNumber&,
                const std::string&,
                const std::string&,
                const std::map<std::string, Amulet::PropertyValueType>&
            >(),
            py::arg("platform"),
            py::arg("version"),
            py::arg("namespace"),
            py::arg("base_name"),
            py::arg("properties") = py::dict()
        );
        Block.def_property_readonly(
            "namespaced_name",
            [](const Amulet::Block& self) {
                return self.get_namespace() + ":" + self.get_base_name();
            },
            py::doc(
                "The namespace:base_name of the blockstate represented by the :class:`Block` object.\n"
                "\n"
                ">>> block: Block\n"
                ">>> block.namespaced_name\n"
                "\n"
                ":return: The namespace:base_name of the blockstate"
            )
        );
        Block.def_property_readonly(
            "namespace",
            &Amulet::Block::get_namespace,
            py::doc(
                "The namespace of the blockstate represented by the :class:`Block` object.\n"
                "\n"
                ">>> block: Block\n"
                ">>> water.namespace\n"
                "\n"
                ":return: The namespace of the blockstate"
            )
        );
        Block.def_property_readonly(
            "base_name",
            &Amulet::Block::get_base_name,
            py::doc(
                "The base name of the blockstate represented by the :class:`Block` object.\n"
                "\n"
                ">>> block: Block\n"
                ">>> block.base_name\n"
                "\n"
                ":return: The base name of the blockstate"
            )
        );
        Block.def_property_readonly(
            "properties",
            &Amulet::Block::get_properties,
            py::doc(
                "The properties of the blockstate represented by the :class:`Block` object as a dictionary.\n"
                ">>> block: Block\n"
                ">>> block.properties\n"
                "\n"
                ":return: A mapping of the properties of the blockstate"
            )
        );
        Block.def(
            "__repr__",
            [](const Amulet::Block& self){
                return "Block(" +
                    py::repr(py::cast(self.get_platform())).cast<std::string>() + ", " +
                    py::repr(py::cast(self.get_version())).cast<std::string>() + ", " +
                    py::repr(py::cast(self.get_namespace())).cast<std::string>() + ", " +
                    py::repr(py::cast(self.get_base_name())).cast<std::string>() + ", " +
                    py::repr(py::cast(self.get_properties())).cast<std::string>() +
                ")";
            }
        );
        Block.def(
            "__hash__",
            [PySorted](const Amulet::Block& self) {
                return py::hash(
                    py::make_tuple(
                        py::cast(self.get_platform()),
                        py::cast(self.get_version()),
                        py::cast(self.get_namespace()),
                        py::cast(self.get_base_name()),
                        py::tuple(PySorted(py::cast(self.get_properties()).attr("items")()))
                    )
                );
            }
        );
        Block.def(
            py::pickle(
                [](const Amulet::Block& self) -> py::bytes {
                    return py::bytes(Amulet::serialise(self));
                },
                [](py::bytes state){
                    return Amulet::deserialise<Amulet::Block>(state.cast<std::string>());
                }
            )
        );

        // TODO: from_string_blockstate, from_snbt_blockstate

        Block.def(py::self == py::self);
        Block.def(py::self != py::self);
        Block.def(py::self > py::self);
        Block.def(py::self < py::self);
        Block.def(py::self >= py::self);
        Block.def(py::self <= py::self);

        // TODO: blockstate, snbt_blockstate

    py::class_<Amulet::BlockStack> BlockStack(m, "BlockStack",
        "A stack of block objects.\n"
        "\n"
        "Java 1.13 added the concept of waterlogging blocks whereby some blocks have a `waterlogged` property.\n"
        "Bedrock achieved the same behaviour by added a layering system which allows the second block to be any block.\n"
        "\n"
        "Amulet supports both implementations with a stack of one or more block objects similar to how Bedrock handles it.\n"
        "Amulet places no restrictions on which blocks can be extra blocks.\n"
        "Extra block may be discarded if the format does not support them.\n"
        "\n"
        "Create a waterlogged stone block.\n"
        ">>> waterlogged_stone = BlockStack(\n"
        ">>>     Block(\"java\", VersionNumber(3578), \"minecraft\", \"stone\"),\n"
        ">>>     Block(\"java\", VersionNumber(3578), \"minecraft\", \"water\", {\"level\": StringTag(\"0\")})\n"
        ">>> )\n"
        "\n"
        "Get a block at an index\n"
        ">>> stone = waterlogged_stone[0]\n"
        ">>> water = waterlogged_stone[1]\n"
        "\n"
        "Get the blocks as a list\n"
        ">>> blocks = list(waterlogged_stone)"
    );
        options.disable_function_signatures();
        BlockStack.def(
            py::init(
                [](Amulet::Block block, py::args py_extra_blocks){
                    std::vector<Amulet::Block> blocks;
                    blocks.push_back(block);
                    std::vector<Amulet::Block> extra_blocks = py_extra_blocks.cast<std::vector<Amulet::Block>>();
                    blocks.insert(blocks.end(), extra_blocks.begin(), extra_blocks.end());
                    return Amulet::BlockStack(blocks);
                }
            ),
            py::doc("__init__(self, block: amulet.block.Block, *extra_blocks: amulet.block.Block) -> None")
        );
        options.enable_function_signatures();

        BlockStack.def(
            "__repr__",
            [](const Amulet::BlockStack& self) {
                const auto& blocks = self.get_blocks();
                std::string repr = "BlockStack(";
                for (size_t i = 0; i < blocks.size(); i++) {
                    if (i != 0) {
                        repr += ", ";
                    }
                    repr += py::repr(py::cast(blocks[i])).cast<std::string>();
                }
                repr += ")";
                return repr;
            }
        );

        BlockStack.def(
            "__len__",
            &Amulet::BlockStack::size
        );

        BlockStack.def(
            "__getitem__",
            &Amulet::BlockStack::operator[]
        );
        BlockStack.def(
            "__hash__",
            [](const Amulet::BlockStack& self) {
                return py::hash(
                    py::tuple(py::cast(self.get_blocks()))
                );
            }
        );

        Amulet::collections_abc::Sequence(m, BlockStack);

        BlockStack.def(py::self == py::self);
        BlockStack.def(py::self != py::self);
        BlockStack.def(py::self > py::self);
        BlockStack.def(py::self < py::self);
        BlockStack.def(py::self >= py::self);
        BlockStack.def(py::self <= py::self);

        BlockStack.def_property_readonly(
            "base_block",
            [](const Amulet::BlockStack& self) -> Amulet::Block {
                return self.get_blocks()[0];
            },
            py::doc(
                "The first block in the stack.\n"
                "\n"
                ">>> waterlogged_stone = BlockStack(\n"
                ">>>     Block(\"java\", VersionNumber(3578), \"minecraft\", \"stone\"),\n"
                ">>>     Block(\"java\", VersionNumber(3578), \"minecraft\", \"water\", {\"level\": StringTag(\"0\")})\n"
                ">>> )\n"
                ">>> waterlogged_stone.base_block\n"
                "Block(\"java\", VersionNumber(3578), \"minecraft\", \"stone\")\n"
                "\n"
                ":return: A Block object"
            )
        );
        BlockStack.def_property_readonly(
            "extra_blocks",
            [](const Amulet::BlockStack& self) -> py::tuple {
                const auto& blocks = self.get_blocks();
                py::tuple py_blocks(blocks.size() - 1);
                for (size_t i = 1; i < blocks.size(); i++) {
                    py_blocks[i - 1] = py::cast(blocks[i]);
                }
                return py_blocks;
            },
            py::doc(
                "The extra blocks in the stack.\n"
                "\n"
                ">>> waterlogged_stone = BlockStack(\n"
                ">>>     Block(\"java\", VersionNumber(3578), \"minecraft\", \"stone\"),\n"
                ">>>     Block(\"java\", VersionNumber(3578), \"minecraft\", \"water\", {\"level\": StringTag(\"0\")})\n"
                ">>> )\n"
                ">>> waterlogged_stone.extra_blocks\n"
                "(Block(\"java\", VersionNumber(3578), \"minecraft\", \"water\", {\"level\": StringTag(\"0\")}),)\n"
                "\n"
                ":return: A tuple of :class:`Block` objects"
            )
        );
}
