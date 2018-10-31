from __future__ import annotations

from sys import getsizeof
import re
from typing import Dict, Iterable, List, Tuple, Union, overload


class MalformedBlockstateException(Exception):
    pass


class Block:
    """
    Class to handle data about various blockstates and allow for extra blocks to be created and interacted with.

    .. note::
        For creating blocks with the ``waterlogged`` property from ``Minecraft: Java Edition`` refer to the note in
        :func:`~Block.get_from_blockstate()`

    Here's a few examples on how create a Block object with extra blocks:

    Creating a new Block object with the base of ``stone`` and has an extra block of ``water[level=1]``:

    >>> stone = Block.get_from_blockstate("minecraft:stone")
    >>> water_level_1 = Block.get_from_blockstate("minecraft:water[level=1]")
    >>> stone_with_extra_block = stone + water_level_1
    >>> repr(stone_with_extra_block)
    'Block(minecraft:stone, minecraft:water[level=1])'


    Creating a new Block object with another layer of extra blocks:

    >>> granite = Block.get_from_blockstate("minecraft:granite")
    >>> stone_water_granite = stone_with_extra_block + granite # Doesn't modify any of the other objects
    >>> repr(stone_water_granite)
    'Block(minecraft:stone, minecraft:water[level=1], minecraft:granite)'


    Creating a new Block object by removing an extra block from all layers:

    *Note: This removes all instances of the Block object from extra blocks*

    >>> stone_granite = stone_water_granite - water_level_1 # Doesn't modify any of the other objects either
    >>> repr(stone_granite)
    'Block(minecraft:stone, minecraft:granite)'


    Creating a new Block object by removing a specific layer:

    >>> oak_log_axis_x = Block.get_from_blockstate("minecraft:oak_log[axis=x]")
    >>> stone_water_granite_water_oak_log = stone_water_granite + water_level_1 + oak_log_axis_x
    >>> repr(stone_water_granite_water_oak_log)
    'Block(minecraft:stone, minecraft:water[level=1], minecraft:granite, minecraft:water[level=1], minecraft:oak_log[axis=x])'

    >>> stone_granite_water_oak_log = stone_water_granite_water_oak_log.remove_layer(0)
    >>> repr(stone_granite_water_oak_log)
    'Block(minecraft:stone, minecraft:granite, minecraft:water[level=1], minecraft:oak_log[axis=x])'

    """

    __slots__ = (
        "_namespace",
        "_base_name",
        "_properties",
        "_extra_blocks",
        "_blockstate",
    )  # Reduces memory footprint

    blockstate_regex = re.compile(
        r"(?:(?P<namespace>[a-z0-9_.-]+):)?(?P<base_name>[a-z0-9/._-]+)(?:\[(?P<property_name>[a-z0-9_]+)=(?P<property_value>[a-z0-9_]+)(?P<properties>.*)\])?"
    )

    parameters_regex = re.compile(r"(?:,(?P<name>[a-z0-9_]+)=(?P<value>[a-z0-9_]+))")

    water = None

    @staticmethod
    def parse_blockstate_string(blockstate: str) -> Tuple[str, str, Dict[str, str]]:
        """
        Parses the supplied blockstate string and returns a tuple containing the namespace, base_name, and property
        dictionary of the blockstate

        :param blockstate: The blockstate string to parse
        :return: The namespace, base_name, and property dictionary of the blockstate
        """

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

        return namespace, base_name, properties

    def __init__(
        self,
        namespace: str,
        base_name: str,
        properties: Dict[str, Union[str, bool, int]],
        extra_blocks: Union[Block, Iterable[Block]] = None,
    ):
        self._namespace = namespace
        self._base_name = base_name
        self._properties = properties
        self._extra_blocks = ()
        if extra_blocks:
            if isinstance(extra_blocks, Block):
                extra_blocks = [extra_blocks]
            self._extra_blocks = tuple(extra_blocks)
        self._blockstate = self._gen_blockstate()

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
    def properties(self) -> Dict[str, Union[str, bool, int]]:
        """
        The mapping of properties of the blockstate represented by the Block object (IE: `{"level": "1"}`)

        :return: A dictionary of the properties of the blockstate
        """
        return self._properties

    @property
    def blockstate(self) -> str:
        """
        The full blockstate string of the blockstate represented by the Block object (IE: `minecraft:stone`, `minecraft:oak_log[axis=x]`)

        :return: The blockstate string
        """
        return self._blockstate

    @property
    def extra_blocks(self) -> Union[Tuple, Tuple[Block]]:
        """
        Returns a tuple of the extra blocks contained in the Block instance

        :return: A tuple of Block objects
        """
        return self._extra_blocks

    def _gen_blockstate(self) -> str:
        blockstate = f"{self._namespace}:{self._base_name}"
        if self._properties:
            props = [f"{key}={value}" for key, value in self._properties.items()]
            blockstate += f"[{','.join(props)}]"
        return blockstate

    def remove_layer(self, layer: int) -> Block:
        """
        Removes the Block object from the specified layer and returns the resulting new Block object

        :param layer: The layer of extra block to remove
        :return: A new instance of Block with the same data but with the extra block at specified layer removed
        """
        return Block(
            self._namespace,
            self._base_name,
            self._properties,
            [*self._extra_blocks[:layer], *self._extra_blocks[layer + 1 :]],
        )

    @classmethod
    def get_from_blockstate(cls, blockstate: str) -> Block:
        """
        Parses a blockstate string and returns a Block object that contains the data for that blockstate.

        .. attention::

            If a blockstate has the ``waterlogged`` property, the property will be removed and if the property was
            ``true``, a water extra block will automatically be added. If the property was ``false``, it'll still be
            removed but no extra block will be added

        :param blockstate: The blockstate string
        :return: A Block object containing the data supplied in the blockstate
        """
        namespace, base_name, properties = cls.parse_blockstate_string(blockstate)

        return cls(namespace, base_name, properties)

    def __str__(self) -> str:
        """
        :return: The base blockstate string of the Block object
        """
        return self._blockstate

    def __repr__(self) -> str:
        """
        :return: The base blockstate string of the Block object along with the blockstate strings of included extra blocks
        """
        return f"Block({', '.join([str(b) for b in (self, *self._extra_blocks)])})"

    def _compare_extra_blocks(self, other: Block) -> bool:
        if len(self._extra_blocks) != len(other._extra_blocks):
            return False

        if len(self._extra_blocks) == 0:
            return True

        for our_extra_block, their_extra_block in zip(
            self._extra_blocks, other._extra_blocks
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

        return (
            self._namespace == other._namespace
            and self._base_name == other._base_name
            and self._properties == other._properties
            and self._compare_extra_blocks(other)
        )

    def __hash__(self) -> int:
        """
        Hashes the Block object

        :return: A hash of the Block object
        """
        current_hash = hash(self._blockstate)

        if self._extra_blocks:
            current_hash = current_hash + hash(self._extra_blocks)

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
            len(other._extra_blocks) == 0
        ):  # Reduces the amount of extra objects/references created
            other_cpy = other
        else:
            other_cpy = Block(other._namespace, other._base_name, other._properties)

        other_extras = []
        for eb in other._extra_blocks:
            if (
                len(eb.extra_blocks) == 0
            ):  # Reduces the amount of extra objects/references created
                other_extras.append(eb)
            else:
                other_extras.append(Block(eb._namespace, eb._base_name, eb._properties))

        return Block(
            self._namespace,
            self._base_name,
            self._properties,
            [*self._extra_blocks, other_cpy, *other_extras],
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
            len(other._extra_blocks) == 0
        ):  # Reduces the amount of extra objects/references created
            other_cpy = other
        else:
            other_cpy = Block(other._namespace, other._base_name, other._properties)

        other_extras = []
        for eb in other._extra_blocks:
            if len(eb.extra_blocks) == 0:
                other_extras.append(eb)
            else:
                other_extras.append(Block(eb._namespace, eb._base_name, eb._properties))

        # Sets are unordered, so a regular set subtraction doesn't always return the order we want (it sometimes will!)
        # So we loop through all of our extra blocks and only append those to the new_extras list if they aren't in
        # extra_blocks_to_remove
        new_extras = []
        extra_blocks_to_remove = (other_cpy, *other_extras)
        for eb in self._extra_blocks:
            if eb not in extra_blocks_to_remove:
                new_extras.append(eb)

        return Block(self._namespace, self._base_name, self._properties, new_extras)

    def __sizeof__(self):
        size = (
            getsizeof(self._namespace)
            + getsizeof(self._base_name)
            + getsizeof(self._properties)
            + getsizeof(self._blockstate)
        )
        for eb in self._extra_blocks:
            size += getsizeof(eb)
        return size


class BlockManager:
    """
    Class to handle the mappings between Block objects and their index-based internal IDs
    """

    def __init__(self):
        """
        Creates a new BlockManager object
        """
        self._index_to_block: List[Block] = []
        self._block_to_index_map: Dict[Block, int] = {}

    @overload
    def __getitem__(self, item: Block) -> int:
        ...

    @overload
    def __getitem__(self, item: int) -> Block:
        ...

    def __getitem__(self, item):
        """
        If a Block object is passed to this function, it'll return the internal ID/index of the
        blockstate. If an int is given, this method will return the Block object at that specified index.

        :param item: The Block object or int to get the mapping data of
        :return: An int if a Block object was supplied, a Block object if an int was supplied
        """
        if isinstance(item, int):
            return self._index_to_block[item]

        if isinstance(item, Block) and item not in self._block_to_index_map:
            self._add_block(item)

        return self._block_to_index_map[item]

    def _add_block(self, block: Block) -> int:
        self._block_to_index_map[block] = i = len(self._block_to_index_map)
        self._index_to_block.append(block)

        return i

    def get_block(self, blockstate: str) -> Block:
        """
        Creates a Block object from the supplied blockstate string, adds the object to the internal mappings, and then
        returns the object.

        :param blockstate: The blockstate string to add
        :return: The Block object created with the supplied blockstate string
        """
        b = Block.get_from_blockstate(blockstate)

        if b not in self._block_to_index_map:
            self._block_to_index_map[b] = len(self._block_to_index_map)
            self._index_to_block.append(b)

        return b


Block.water = Block("minecraft", "water", {})
