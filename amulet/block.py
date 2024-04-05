from __future__ import annotations

import re
from typing import Union, Self, Callable, cast, Any, overload
from types import MappingProxyType
from collections.abc import Iterator, Sequence, Hashable, Mapping

from amulet_nbt import ByteTag, ShortTag, IntTag, LongTag, StringTag, from_snbt

from amulet.version import (
    PlatformVersionContainer,
    VersionNumber,
)

PropertyValueType = Union[
    ByteTag,
    ShortTag,
    IntTag,
    LongTag,
    StringTag,
]
PropertyType = Mapping[str, PropertyValueType]
PropertyTypeMultiple = dict[str, tuple[PropertyValueType, ...]]

PropertyValueClasses = (
    ByteTag,
    ShortTag,
    IntTag,
    LongTag,
    StringTag,
)

_BlockstatePattern = re.compile(
    r"((?P<namespace>[a-z0-9_.-]+):)?"
    r"(?P<base_name>[a-z0-9/._-]+)"
    r"(\[(?P<properties>.*?)])?"
)

_PropertiesPattern = re.compile(r"(?P<name>[a-zA-Z0-9_]+)=(?P<value>[a-zA-Z0-9_]+),?")
_SNBTPropertiesPattern = re.compile(
    r"(?P<name>[a-zA-Z0-9_]+)=(?P<value>[a-zA-Z0-9_\"']+),?"
)


class BlockProperties(Mapping[str, PropertyValueType], Hashable):
    """An immutable and hashable mapping from strings to nbt objects."""

    _properties: Mapping[str, PropertyValueType]
    _hash: int | None

    __slots__ = (
        "_properties",
        "_hash",
    )

    def __init__(self, properties: Mapping[str, PropertyValueType]):
        self._properties = dict(properties)
        if not all(isinstance(k, str) for k in self._properties.keys()):
            raise TypeError("keys must be strings")
        if not all(
            isinstance(v, PropertyValueClasses) for v in self._properties.values()
        ):
            raise TypeError("values must be nbt")
        self._hash = None

    def __getstate__(self) -> Any:
        return self._properties

    def __setstate__(self, state: Any) -> None:
        self._properties = state
        self._hash = None

    def __getitem__(self, key: str) -> PropertyValueType:
        return self._properties[key]

    def __len__(self) -> int:
        return len(self._properties)

    def __iter__(self) -> Iterator[str]:
        return iter(self._properties)

    def __hash__(self) -> int:
        if self._hash is None:
            self._hash = hash(tuple(sorted(self._properties.items())))
        return self._hash


class Block(PlatformVersionContainer):
    """
    A class to manage the state of a block.

    It is an immutable object that contains a namespace, base name and properties and optionally a version.

    Here's a few examples on how create a Block object:

    >>> # Create a block with the namespace `minecraft` and base name `stone`
    >>> stone = Block("java", VersionNumber(3578), "minecraft", "stone")

    >>> # Create a water block with the level property
    >>> water = Block(
    >>>     "java", VersionNumber(3578),
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

    _hash: int | None

    __slots__ = (
        "_namespace",
        "_base_name",
        "_properties",
        "_hash",
    )

    def __init__(
        self,
        platform: str,
        version: VersionNumber,
        namespace: str,
        base_name: str,
        properties: PropertyType = MappingProxyType({}),
    ):
        """
        Constructs a :class:`Block` instance.

        >>> stone = Block("java", VersionNumber(3578), "minecraft", "stone")
        >>>
        >>> # Create a water block with the level property
        >>> water = Block(
        >>>     "java", VersionNumber(3578),
        >>>     "minecraft",  # the namespace
        >>>     "water",  # the base name
        >>>     {  # A dictionary of properties.
        >>>         # Keys must be strings and values must be a numerical or string NBT type.
        >>>         "level": StringTag("0")  # define a property `level` with a string value `1`
        >>>     }
        >>> )

        :param version: The game version this block is defined in.
        :param namespace: The string namespace of the block. eg `minecraft`
        :param base_name: The string base name of the block. eg `stone`
        :param properties: A mapping. Keys must be strings and values must be a numerical or string NBT type.
        """
        super().__init__(platform, version)
        self._namespace = str(namespace)
        self._base_name = str(base_name)
        self._properties = BlockProperties(properties)
        self._hash = None

    def __getstate__(self) -> tuple[Any, ...]:
        return *super().__getstate__(), self._namespace, self._base_name, self._properties

    def __setstate__(self, state: tuple[Any, ...]) -> tuple[Any, ...]:
        self._namespace, self._base_name, self._properties, *state = super().__setstate__(state)
        self._hash = None
        return state

    @classmethod
    def from_string_blockstate(
        cls, platform: str, version: VersionNumber, blockstate: str
    ) -> Self:
        """
        Parse a Java format blockstate where values are all strings and populate a :class:`Block` class with the data.

        >>> stone = Block.from_string_blockstate("minecraft:stone")
        >>> water = Block.from_string_blockstate("minecraft:water[level=0]")

        :param version: The version the block is defined in.
        :param blockstate: The Java blockstate string to parse.
        :return: A Block instance containing the state.
        """
        namespace, block_name, properties = cls._parse_blockstate_string(blockstate)
        return cls(platform, version, namespace, block_name, properties)

    @classmethod
    def from_snbt_blockstate(
        cls, platform: str, version: VersionNumber, blockstate: str
    ) -> Self:
        """
        Parse a blockstate where values are SNBT of any type and populate a :class:`Block` class with the data.
        """
        namespace, block_name, properties = cls._parse_blockstate_string(
            blockstate, True
        )
        return cls(platform, version, namespace, block_name, properties)

    @staticmethod
    def _parse_blockstate_string(
        blockstate: str, snbt: bool = False
    ) -> tuple[str, str, PropertyType]:
        """
        Parse a Java or SNBT blockstate string and return the raw data.

        To parse the blockstate and return a :class:`Block` instance use :func:`from_string_blockstate` or :func:`from_snbt_blockstate`

        :param blockstate: The blockstate to parse
        :param snbt: Are the property values in SNBT format. If false all values must be an instance of :class:`~StringTag`
        :return: namespace, block_name, properties

        """
        match = _BlockstatePattern.fullmatch(blockstate)
        if match is None:
            raise ValueError(f"Invalid blockstate {blockstate}")
        namespace = match.group("namespace") or "minecraft"
        base_name = match.group("base_name")

        properties_str = match.group("properties")
        properties = {}

        wrapper: Callable[[str], PropertyValueType]

        if snbt:
            pattern = _SNBTPropertiesPattern
            wrapper = cast(Callable[[str], PropertyValueType], from_snbt)
        else:
            pattern = _PropertiesPattern
            wrapper = StringTag

        while properties_str:
            match = pattern.match(properties_str)
            if match is None:
                raise ValueError(f"Invalid blockstate {blockstate}")
            properties[match.group("name")] = wrapper(match.group("value"))
            properties_str = properties_str[match.end() :]

        return (
            namespace,
            base_name,
            properties,
        )

    def __hash__(self) -> int:
        if self._hash is None:
            self._hash = hash(self.__getstate__())
        return self._hash

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Block):
            return NotImplemented
        return self.__getstate__() == other.__getstate__()

    def __gt__(self, other: Block) -> bool:
        if not isinstance(other, Block):
            return NotImplemented
        return hash(self) > hash(other)

    def __lt__(self, other: Block) -> bool:
        if not isinstance(other, Block):
            return NotImplemented
        return hash(self) < hash(other)

    def __repr__(self) -> str:
        return f"Block({self.platform!r}, {self.version!r}, {self.namespace!r}, {self.base_name!r}, {dict(self.properties)!r})"

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
    def blockstate(self) -> str:
        """
        The Java blockstate string of this :class:`Block` object
        Note this will only contain properties with StringTag values.

        >>> stone = Block("java", VersionNumber(3578), "minecraft", "stone")
        >>> stone.blockstate
        'minecraft:stone'
        >>> water = Block("java", VersionNumber(3578), "minecraft", "water", {"level": StringTag("0")})
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

        >>> bell = Block(
        >>>     "java", VersionNumber(3578),
        >>>     "minecraft",
        >>>     "bell",
        >>>     {
        >>>         "attachment":StringTag("standing"),
        >>>         "direction":IntTag(0),
        >>>         "toggle_bit":ByteTag(0)
        >>>     }
        >>> )
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
    >>>     Block("java", VersionNumber(3578), "minecraft", "stone"),
    >>>     Block("java", VersionNumber(3578), "minecraft", "water", {"level": StringTag("0")})
    >>> )

    Get a block at an index
    >>> stone = waterlogged_stone[0]
    >>> water = waterlogged_stone[1]

    Get the blocks as a list
    >>> blocks = list(waterlogged_stone)
    """

    _blocks: tuple[Block, ...]
    _hash: int | None

    __slots__ = ("_blocks", "_hash")

    def __init__(self, block: Block, *extra_blocks: Block):
        self._blocks = (block, *extra_blocks)
        if not all(isinstance(block, Block) for block in self._blocks):
            raise TypeError
        self._hash = None

    def __repr__(self) -> str:
        return f"BlockStack({', '.join(map(repr, self._blocks))})"

    def __len__(self) -> int:
        return len(self._blocks)

    @overload
    def __getitem__(self, index: int) -> Block: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[Block]: ...

    def __getitem__(self, item: int | slice) -> Block | Sequence[Block]:
        return self._blocks[item]

    def __hash__(self) -> int:
        if self._hash is None:
            self._hash = hash(self._blocks)
        return self._hash

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, BlockStack):
            return NotImplemented
        return self._blocks == other._blocks

    @property
    def base_block(self) -> Block:
        """
        The first block in the stack.

        >>> waterlogged_stone = BlockStack(
        >>>     Block("java", VersionNumber(3578), "minecraft", "stone"),
        >>>     Block("java", VersionNumber(3578), "minecraft", "water", {"level": StringTag("0")})
        >>> )
        >>> waterlogged_stone.base_block
        Block("java", VersionNumber(3578), "minecraft", "stone")

        :return: A Block object
        """
        return self._blocks[0]

    @property
    def extra_blocks(self) -> tuple[Block, ...]:
        """
        The extra blocks in the stack.

        >>> waterlogged_stone = BlockStack(
        >>>     Block("java", VersionNumber(3578), "minecraft", "stone"),
        >>>     Block("java", VersionNumber(3578), "minecraft", "water", {"level": StringTag("0")})
        >>> )
        >>> waterlogged_stone.extra_blocks
        (Block("java", VersionNumber(3578), "minecraft", "water", {"level": StringTag("0")}),)

        :return: A tuple of :class:`Block` objects
        """
        return self._blocks[1:]
