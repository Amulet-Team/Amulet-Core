from __future__ import annotations

import re
from typing import Union, Optional
from types import MappingProxyType
from collections.abc import Iterator, Sequence, Hashable, Mapping

from amulet_nbt import ByteTag, ShortTag, IntTag, LongTag, StringTag, from_snbt

from amulet.game_version import AbstractGameVersion

PropertyValueType = Union[
    ByteTag,
    ShortTag,
    IntTag,
    LongTag,
    StringTag,
]
PropertyType = Mapping[str, PropertyValueType]
PropertyTypeMultiple = dict[str, tuple[PropertyValueType, ...]]

PropertyDataTypes = (
    ByteTag,
    ShortTag,
    IntTag,
    LongTag,
    StringTag,
)

_SNBTBlockstatePattern = re.compile(
    r"(?:(?P<namespace>[a-z0-9_.-]+):)?(?P<base_name>[a-z0-9/._-]+)(?:\[(?P<property_name>[a-z0-9_]+)=(?P<property_value>[a-z0-9_\"']+)(?P<properties>.*)\])?"
)
_BlockstatePattern = re.compile(
    r"(?:(?P<namespace>[a-z0-9_.-]+):)?(?P<base_name>[a-z0-9/._-]+)(?:\[(?P<property_name>[a-z0-9_]+)=(?P<property_value>[a-z0-9_]+)(?P<properties>.*)\])?"
)

_SNBTPropertiesPattern = re.compile(
    r"(?:,(?P<name>[a-z0-9_]+)=(?P<value>[a-z0-9_\"']+))"
)
_PropertiesPattern = re.compile(r"(?:,(?P<name>[a-z0-9_]+)=(?P<value>[a-z0-9_]+))")


class BlockProperties(Mapping[str, PropertyValueType], Hashable):
    """An immutable and hashable mapping from strings to nbt objects."""

    def __init__(self, properties: Mapping[str, PropertyValueType]):
        self._properties = dict(properties)
        if not all(isinstance(k, str) for k in self._properties.keys()):
            raise TypeError("keys must be strings")
        if not all(isinstance(v, PropertyDataTypes) for v in self._properties.values()):
            raise TypeError("values must be nbt")
        self._hash = hash(sorted(self._properties.items()))

    def __getitem__(self, key: str) -> PropertyValueType:
        return self._properties[key]

    def __len__(self) -> int:
        return len(self._properties)

    def __iter__(self) -> Iterator[str]:
        return iter(self._properties)

    def __hash__(self) -> int:
        return self._hash


class Block:
    """
    A class to manage the state of a block.

    It is an immutable object that contains a namespace, base name and properties and optionally a version.

    Here's a few examples on how create a Block object:

    >>> # Create a block with the namespace `minecraft` and base name `stone`
    >>> stone = Block("minecraft", "stone")

    >>> # Create a water block with the level property
    >>> water = Block(
    >>>     "minecraft",  # the namespace
    >>>     "water",  # the base name
    >>>     {  # A dictionary of properties.
    >>>         # Keys must be strings and values must be a numerical or string NBT type.
    >>>         "level": StringTag("0")  # define a property `level` with a string value `1`
    >>>     }
    >>> )

    >>> # The above two examples can also be achieved by creating the block from the Java blockstate.
    >>> stone = Block.from_string_blockstate("minecraft:stone")
    >>> water = Block.from_string_blockstate("minecraft:water[level=0]")
    """

    __slots__ = (
        "_namespaced_name",
        "_namespace",
        "_base_name",
        "_properties",
        "_version",
    )

    def __init__(
        self,
        namespace: str,
        base_name: str,
        properties: PropertyType = MappingProxyType({}),
        version: Optional[AbstractGameVersion] = None,
    ):
        """
        Constructs a :class:`Block` instance.

        >>> stone = Block("minecraft", "stone")
        >>>
        >>> # Create a water block with the level property
        >>> water = Block(
        >>>     "minecraft",  # the namespace
        >>>     "water",  # the base name
        >>>     {  # A dictionary of properties.
        >>>         # Keys must be strings and values must be a numerical or string NBT type.
        >>>         "level": StringTag("0")  # define a property `level` with a string value `1`
        >>>     }
        >>> )

        :param namespace: The string namespace of the block. eg `minecraft`
        :param base_name: The string base name of the block. eg `stone`
        :param properties: A mapping. Keys must be strings and values must be a numerical or string NBT type.
        :param version: The game version this block is defined in.
            If omitted/None it will default to the highest version the container it is used in supports.
        """
        self._namespace = str(namespace)
        self._base_name = str(base_name)
        self._properties = BlockProperties(properties)
        if version is not None and not isinstance(version, AbstractGameVersion):
            raise TypeError("Invalid version", version)
        self._version = version

    @classmethod
    def from_string_blockstate(cls, blockstate: str):
        """
        Parse a Java format blockstate where values are all strings and populate a :class:`Block` class with the data.

        >>> stone = Block.from_string_blockstate("minecraft:stone")
        >>> water = Block.from_string_blockstate("minecraft:water[level=0]")

        :param blockstate: The Java blockstate string to parse.
        :return: A Block instance containing the state.
        """
        namespace, block_name, properties = cls.parse_blockstate_string(blockstate)
        return cls(namespace, block_name, properties)

    @classmethod
    def from_snbt_blockstate(cls, blockstate: str):
        """
        Parse a blockstate where values are SNBT of any type and populate a :class:`Block` class with the data.
        """
        namespace, block_name, properties = cls.parse_blockstate_string(
            blockstate, True
        )
        return cls(namespace, block_name, properties)

    @staticmethod
    def parse_blockstate_string(
        blockstate: str, snbt: bool = False
    ) -> tuple[str, str, PropertyType]:
        """
        Parse a Java or SNBT blockstate string and return the raw data.

        To parse the blockstate and return a :class:`Block` instance use :func:`from_string_blockstate` or :func:`from_snbt_blockstate`

        :param blockstate: The blockstate to parse
        :param snbt: Are the property values in SNBT format. If false all values must be an instance of :class:`~StringTag`
        :return: namespace, block_name, properties

        """
        if snbt:
            match = _SNBTBlockstatePattern.match(blockstate)
        else:
            match = _BlockstatePattern.match(blockstate)
        namespace = match.group("namespace") or "minecraft"
        base_name = match.group("base_name")

        if match.group("property_name") is not None:
            properties = {match.group("property_name"): match.group("property_value")}
            properties_string = match.group("properties")
            if properties_string is not None:
                if snbt:
                    for match in _SNBTPropertiesPattern.finditer(properties_string):
                        properties[match.group("name")] = match.group("value")
                else:
                    for match in _PropertiesPattern.finditer(properties_string):
                        properties[match.group("name")] = match.group("value")
        else:
            properties = {}

        if snbt:
            properties_dict = {k: from_snbt(v) for k, v in sorted(properties.items())}
        else:
            properties_dict = {k: StringTag(v) for k, v in sorted(properties.items())}

        return (
            namespace,
            base_name,
            properties_dict,
        )

    def _data(self):
        return self._namespace, self._base_name, self._properties, self._version

    def __hash__(self):
        return hash(self._data())

    def __eq__(self, other):
        if not isinstance(other, Block):
            return NotImplemented
        return self._data() == other._data()

    def __gt__(self, other):
        if not isinstance(other, Block):
            return NotImplemented
        return hash(self) > hash(other)

    def __lt__(self, other):
        if not isinstance(other, Block):
            return NotImplemented
        return hash(self) < hash(other)

    def __repr__(self):
        return f"Block({self.namespace!r}, {self.base_name!r}, {dict(self.properties)!r}, {self.version!r})"

    @property
    def namespaced_name(self) -> str:
        """
        The namespace:base_name of the blockstate represented by the :class:`Block` object.

        >>> water = Block.from_string_blockstate("minecraft:water[level=0]")
        >>> water.namespaced_name
        'minecraft:water'

        :return: The namespace:base_name of the blockstate
        """
        return f"{self.namespace}:{self.base_name}"

    @property
    def namespace(self) -> str:
        """
        The namespace of the blockstate represented by the :class:`Block` object.

        >>> water = Block.from_string_blockstate("minecraft:water[level=0]")
        >>> water.namespace
        'minecraft'

        :return: The namespace of the blockstate
        """
        return self._namespace

    @property
    def base_name(self) -> str:
        """
        The base name of the blockstate represented by the :class:`Block` object.

        >>> water = Block.from_string_blockstate("minecraft:water[level=0]")
        >>> water.base_name
        'water'

        :return: The base name of the blockstate
        """
        return self._base_name

    @property
    def properties(self) -> BlockProperties:
        """
        The mapping of properties of the blockstate represented by the :class:`Block` object.
        >>> water = Block.from_string_blockstate("minecraft:water[level=0]")
        >>> water.properties
        {"level": StringTag("0")}
        :return: A mapping of the properties of the blockstate
        """
        return self._properties

    @property
    def version(self) -> Optional[AbstractGameVersion]:
        """
        The game version this block was defined in.
        Note that this may be None.
        """
        return self._version

    @property
    def blockstate(self) -> str:
        """
        The Java blockstate string of this :class:`Block` object
        Note this will only contain properties with StringTag values.

        >>> stone = Block("minecraft", "stone")
        >>> stone.blockstate
        'minecraft:stone'
        >>> water = Block("minecraft", "water", {"level": StringTag("0")})
        >>> water.blockstate
        `minecraft:water[level=0]`

        :return: The blockstate string
        """
        blockstate = self.namespaced_name
        if self.properties:
            props = [
                f"{key}={value.py_str}"
                for key, value in sorted(self.properties.items())
                if isinstance(value, StringTag)
            ]
            blockstate += f"[{','.join(props)}]"
        return blockstate

    @property
    def snbt_blockstate(self) -> str:
        """
        A modified version of the Java blockstate format that supports all NBT types.
        Converts the property values to the SNBT format to preserve type.
        Note if there are extra blocks this will only show the base block.

        >>> bell = Block("minecraft", "bell", {
        >>>     "attachment":StringTag("standing"),
        >>>     "direction":IntTag(0),
        >>>     "toggle_bit":ByteTag(0)
        >>> })
        >>> bell.snbt_blockstate
        'minecraft:bell[attachment="standing",direction=0,toggle_bit=0b]'

        :return: The SNBT blockstate string
        """
        snbt_blockstate = self.namespaced_name
        if self.properties:
            props = [
                f"{key}={value.to_snbt()}"
                for key, value in sorted(self.properties.items())
            ]
            snbt_blockstate += f"[{','.join(props)}]"
        return snbt_blockstate


class BlockStack(Sequence[Block]):
    """
    A stack of block objects.

    Java 1.13 added the concept of waterlogging blocks whereby some blocks have a `waterlogged` property.
    Bedrock achieved the same behaviour by added a layering system which allows the second block to be any block.

    Amulet supports both implementations with a stack of one or more block objects similar to how Bedrock handles it.
    Amulet places no restrictions on which blocks can be extra blocks.
    Extra block may be discarded if the format does not support them.

    Create a waterlogged stone block.
    >>> waterlogged_stone = BlockStack(
    >>>     Block("minecraft", "stone"),
    >>>     Block("minecraft", "water", {"level": StringTag("0")})
    >>> )

    Get a block at an index
    >>> stone = waterlogged_stone[0]
    >>> water = waterlogged_stone[1]

    Get the blocks as a list
    >>> blocks = list(waterlogged_stone)
    """

    __slots__ = ("_blocks",)

    def __init__(self, block: Block, *extra_blocks: Block):
        self._blocks = (block, *extra_blocks)
        if not all(isinstance(block, Block) for block in self._blocks):
            raise TypeError

    def __len__(self) -> int:
        return len(self._blocks)

    def __getitem__(self, item):
        return self._blocks[item]

    @property
    def base_block(self) -> Block:
        """
        The first block in the stack.

        >>> waterlogged_stone = BlockStack(
        >>>     Block("minecraft", "stone"),
        >>>     Block("minecraft", "water", {"level": StringTag("0")})
        >>> )
        >>> waterlogged_stone.base_block
        Block("minecraft", "stone")

        :return: A Block object
        """
        return self._blocks[0]

    @property
    def extra_blocks(self) -> tuple[Block, ...]:
        """
        The extra blocks in the stack.

        >>> waterlogged_stone = BlockStack(
        >>>     Block("minecraft", "stone"),
        >>>     Block("minecraft", "water", {"level": StringTag("0")})
        >>> )
        >>> waterlogged_stone.extra_blocks
        (Block("minecraft", "water", {"level": StringTag("0")}),)

        :return: A tuple of :class:`Block` objects
        """
        return self._blocks[1:]
