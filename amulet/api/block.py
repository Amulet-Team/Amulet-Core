from __future__ import annotations

import copy
from sys import getsizeof
import re
from typing import Dict, Iterable, Tuple, Union
import amulet_nbt

from .errors import InvalidBlockException

PropertyValueType = Union[
    amulet_nbt.TAG_Byte,
    amulet_nbt.TAG_Short,
    amulet_nbt.TAG_Int,
    amulet_nbt.TAG_Long,
    amulet_nbt.TAG_String,
]
PropertyType = Dict[str, PropertyValueType]

PropertyDataTypes = (
    amulet_nbt.TAG_Byte,
    amulet_nbt.TAG_Short,
    amulet_nbt.TAG_Int,
    amulet_nbt.TAG_Long,
    amulet_nbt.TAG_String,
)


def blockstate_to_block(blockstate: str) -> "Block":
    namespace, base_name, properties = Block.parse_blockstate_string(blockstate)
    return Block(namespace=namespace, base_name=base_name, properties=properties)


class Block:
    """
    Class to handle data about various blockstates and allow for extra blocks to be created and interacted with.

    .. important::
       Creating version specific block objects via the `Block()` constructor instead of using
       :meth:`api.world.World.get_block_instance` is supported but not encouraged. To avoid possible caveats of doing this,
       make sure to either only instantiate blocks with Amulet blockstate data or use
       :meth:`api.world.World.get_block_instance` instead

    Here's a few examples on how create a Block object with extra blocks:

    Creating a new Block object with the base of ``stone`` and has an extra block of ``water[level=1]``:

    >>> stone = blockstate_to_block("minecraft:stone")
    >>> water_level_1 = blockstate_to_block("minecraft:water[level=1]")
    >>> stone_with_extra_block = stone + water_level_1
    >>> repr(stone_with_extra_block)
    'Block(minecraft:stone, minecraft:water[level=1])'

    Creating a new Block object using the namespace and base_name:

    >>> granite = Block(namespace="minecraft", base_name="granite")


    Creating a new Block object with another layer of extra blocks:

    >>> stone_water_granite = stone_with_extra_block + granite # Doesn't modify any of the other objects
    >>> repr(stone_water_granite)
    'Block(minecraft:stone, minecraft:water[level=1], minecraft:granite)'


    Creating a new Block object by removing an extra block from all layers:

    *Note: This removes all instances of the Block object from extra blocks*

    >>> stone_granite = stone_water_granite - water_level_1 # Doesn't modify any of the other objects either
    >>> repr(stone_granite)
    'Block(minecraft:stone, minecraft:granite)'


    Creating a new Block object by removing a specific layer:

    >>> oak_log_axis_x = blockstate_to_block("minecraft:oak_log[axis=x]")
    >>> stone_water_granite_water_oak_log = stone_water_granite + water_level_1 + oak_log_axis_x
    >>> repr(stone_water_granite_water_oak_log)
    'Block(minecraft:stone, minecraft:water[level=1], minecraft:granite, minecraft:water[level=1], minecraft:oak_log[axis=x])'

    >>> stone_granite_water_oak_log = stone_water_granite_water_oak_log.remove_layer(0)
    >>> repr(stone_granite_water_oak_log)
    'Block(minecraft:stone, minecraft:granite, minecraft:water[level=1], minecraft:oak_log[axis=x])'

    """

    __slots__ = (
        "_namespaced_name",
        "_namespace",
        "_base_name",
        "_properties",
        "_extra_blocks",
        "_blockstate",
    )  # Reduces memory footprint

    blockstate_regex = re.compile(
        r"(?:(?P<namespace>[a-z0-9_.-]+):)?(?P<base_name>[a-z0-9/._-]+)(?:\[(?P<property_name>[a-z0-9_]+)=(?P<property_value>[a-z0-9_\"]+)(?P<properties>.*)\])?"
    )
    # blockstate_regex = re.compile(
    #     r"(?:(?P<namespace>[a-z0-9_.-]+):)?(?P<base_name>[a-z0-9/._-]+)(?:\[(?P<property_name>[a-z0-9_]+)=(?P<property_value>[a-z0-9_]+)(?P<properties>.*)\])?"
    # )

    parameters_regex = re.compile(r"(?:,(?P<name>[a-z0-9_]+)=(?P<value>[a-z0-9_\"]+))")

    # parameters_regex = re.compile(r"(?:,(?P<name>[a-z0-9_]+)=(?P<value>[a-z0-9_]+))")

    def __init__(
        self,
        namespace: str,
        base_name: str,
        properties: PropertyType = None,
        extra_blocks: Union[Block, Iterable[Block]] = None,
    ):
        self._blockstate = None
        self._namespaced_name = None
        assert (isinstance(namespace, str) or namespace is None) and isinstance(
            base_name, str
        ), f"namespace and base_name must be strings {namespace} {base_name}"
        self._namespace = namespace
        self._base_name = base_name

        if properties is None:
            properties = {}
        assert isinstance(properties, dict) and all(
            isinstance(val, PropertyDataTypes) for val in properties.values()
        ), properties

        self._properties = properties
        self._extra_blocks = ()
        if extra_blocks:
            if isinstance(extra_blocks, Block):
                extra_blocks = [extra_blocks]
            self._extra_blocks = tuple(extra_blocks)

        self._gen_blockstate()

    @property
    def namespaced_name(self) -> str:
        """
        The namespace:base_name of the blockstate represented by the Block object (IE: `minecraft:stone`)

        :return: The namespace:base_name of the blockstate
        """
        return self._namespaced_name

    @property
    def namespace(self) -> str:
        """
        The namespace of the blockstate represented by the Block object (IE: `minecraft`)

        :return: The namespace of the blockstate
        """
        return self._namespace

    @property
    def base_name(self) -> str:
        """
        The base name of the blockstate represented by the Block object (IE: `stone`, `dirt`)

        :return: The base name of the blockstate
        """
        return self._base_name

    @property
    def properties(self) -> PropertyType:
        """
        The mapping of properties of the blockstate represented by the Block object (IE: `{"level": "1"}`)

        :return: A dictionary of the properties of the blockstate
        """
        return copy.deepcopy(self._properties)

    @property
    def blockstate(self) -> str:
        """
        The full blockstate string of the blockstate represented by the Block object (IE: `minecraft:stone`, `minecraft:oak_log[axis=x]`)

        :return: The blockstate string
        """
        return self._blockstate

    @property
    def base_block(self) -> Block:
        """
        Returns the block without any extra blocks

        :return: A Block object
        """
        if len(self.extra_blocks) == 0:
            return self
        else:
            return Block(
                namespace=self.namespace,
                base_name=self.base_name,
                properties=self.properties,
            )

    @property
    def extra_blocks(self) -> Tuple[Block, ...]:
        """
        Returns a tuple of the extra blocks contained in the Block instance

        :return: A tuple of Block objects
        """
        return self._extra_blocks

    @property
    def block_tuple(self) -> Tuple[Block, ...]:
        """
        Returns the stack of blocks represented by this object as a tuple.
        This is a tuple of base_block and extra_blocks
        :return: A tuple of Block objects
        """
        return (self.base_block,) + self.extra_blocks

    def _gen_blockstate(self):
        self._namespaced_name = self._blockstate = f"{self.namespace}:{self.base_name}"
        if self.properties:
            props = [
                f"{key}={value.to_snbt()}"
                for key, value in sorted(self.properties.items())
            ]
            self._blockstate += f"[{','.join(props)}]"
        if self.extra_blocks:
            self._blockstate += (
                f"{{{' , '.join(block.blockstate for block in self.extra_blocks)}}}"
            )

    @staticmethod
    def parse_blockstate_string(
        blockstate: str,
    ) -> Tuple[str, str, PropertyType]:
        match = Block.blockstate_regex.match(blockstate)
        namespace = match.group("namespace") or "minecraft"
        base_name = match.group("base_name")

        if match.group("property_name") is not None:
            properties = {match.group("property_name"): match.group("property_value")}
        else:
            properties = {}

        properties_string = match.group("properties")
        if properties_string is not None:
            properties_match = Block.parameters_regex.finditer(properties_string)
            for match in properties_match:
                properties[match.group("name")] = match.group("value")

        return (
            namespace,
            base_name,
            {k: amulet_nbt.from_snbt(v) for k, v in sorted(properties.items())},
        )

    def __str__(self) -> str:
        """
        :return: The base blockstate string of the Block object
        """
        return self.blockstate

    def __repr__(self) -> str:
        """
        :return: The base blockstate string of the Block object along with the blockstate strings of included extra blocks
        """
        return f"Block({', '.join([str(b) for b in (self, *self.extra_blocks)])})"

    def __len__(self):
        return len(self._extra_blocks) + 1

    def _compare_extra_blocks(self, other: Block) -> bool:
        if len(self.extra_blocks) != len(other.extra_blocks):
            return False

        if len(self.extra_blocks) == 0:
            return True

        for our_extra_block, their_extra_block in zip(
            self.extra_blocks, other.extra_blocks
        ):
            if our_extra_block != their_extra_block:
                return False

        return True

    def __eq__(self, other: Block) -> bool:
        """
        Checks the equality of this Block object to another Block object

        :param other: The Block object to check against
        :return: True if the Blocks objects are equal, False otherwise
        """
        if self.__class__ != other.__class__:
            return False

        return self.blockstate == other.blockstate and self._compare_extra_blocks(other)

    def __gt__(self, other: Block) -> bool:
        """
        Allows blocks to be sorted so numpy.unique can be used on them
        """
        if self.__class__ != other.__class__:
            return False
        return self.blockstate > other.blockstate

    def __hash__(self) -> int:
        """
        Hashes the Block object

        :return: A hash of the Block object
        """
        current_hash = hash(self.blockstate)

        if self.extra_blocks:
            current_hash = current_hash + hash(self.extra_blocks)

        return current_hash

    def __add__(self, other: Block) -> Block:
        """
        Allows for other Block objects to be added to this Block object's ``extra_blocks``

        :param other: The Block object to add to the end of this Block object's `extra_blocks`
        :return: A new Block object with the same data but with an additional Block at the end of ``extra_blocks``
        """
        if not isinstance(other, Block):
            return NotImplemented

        if (
            len(other.extra_blocks) == 0
        ):  # Reduces the amount of extra objects/references created
            other_cpy = other
        else:
            other_cpy = Block(
                namespace=other.namespace,
                base_name=other.base_name,
                properties=other.properties,
            )

        other_extras = []
        for eb in other.extra_blocks:
            if (
                len(eb.extra_blocks) == 0
            ):  # Reduces the amount of extra objects/references created
                other_extras.append(eb)
            else:
                other_extras.append(
                    Block(
                        namespace=eb.namespace,
                        base_name=eb.base_name,
                        properties=eb.properties,
                    )
                )

        return Block(
            namespace=self.namespace,
            base_name=self.base_name,
            properties=self.properties,
            extra_blocks=[*self.extra_blocks, other_cpy, *other_extras],
        )

    def __sub__(self, other: Block) -> Block:
        """
        Allows for other Block objects to be subtracted from this Block object's ``extra_blocks``

        :param other: The Block object to subtract from this Block objects' ``extra_blocks``
        :return: A new Block object without any instances of the subtracted block in ``extra_blocks``
        """
        if not isinstance(other, Block):
            return NotImplemented

        if (
            len(other.extra_blocks) == 0
        ):  # Reduces the amount of extra objects/references created
            other_cpy = other
        else:
            other_cpy = Block(
                namespace=other.namespace,
                base_name=other.base_name,
                properties=other.properties,
            )

        other_extras = []
        for eb in other.extra_blocks:
            if len(eb.extra_blocks) == 0:
                other_extras.append(eb)
            else:
                other_extras.append(
                    Block(
                        namespace=eb.namespace,
                        base_name=eb.base_name,
                        properties=eb.properties,
                    )
                )

        # Sets are unordered, so a regular set subtraction doesn't always return the order we want (it sometimes will!)
        # So we loop through all of our extra blocks and only append those to the new_extras list if they aren't in
        # extra_blocks_to_remove
        new_extras = []
        extra_blocks_to_remove = (other_cpy, *other_extras)
        for eb in self.extra_blocks:
            if eb not in extra_blocks_to_remove:
                new_extras.append(eb)

        return Block(
            namespace=self.namespace,
            base_name=self.base_name,
            properties=self.properties,
            extra_blocks=new_extras,
        )

    def remove_layer(self, layer: int) -> Block:
        """
        Removes the Block object from the specified layer and returns the resulting new Block object

        :param layer: The layer of extra block to remove
        :return: A new instance of Block with the same data but with the extra block at specified layer removed
        :raises `InvalidBlockException`: Raised when you remove the base block from a Block with no other extra blocks
        """
        if layer == 0 and len(self.extra_blocks) > 0:
            new_base = self._extra_blocks[0]
            return Block(
                namespace=new_base.namespace,
                base_name=new_base.base_name,
                properties=new_base.properties,
                extra_blocks=[*self._extra_blocks[1:]],
            )
        elif layer > len(self.extra_blocks):
            raise InvalidBlockException("You cannot remove a non-existant layer")
        elif layer == 0:
            raise InvalidBlockException(
                "Removing the base block with no extra blocks is not supported"
            )

        return Block(
            namespace=self.namespace,
            base_name=self.base_name,
            properties=self.properties,
            extra_blocks=[*self.extra_blocks[: layer - 1], *self.extra_blocks[layer:]],
        )

    def __sizeof__(self):
        size = (
            getsizeof(self.namespace)
            + getsizeof(self.base_name)
            + getsizeof(self.properties)
            + getsizeof(self.blockstate)
        )
        for eb in self.extra_blocks:
            size += getsizeof(eb)
        return size
