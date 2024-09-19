from __future__ import annotations

import collections.abc
import types
import typing

import amulet.version
import amulet_nbt

__all__ = ["Block", "BlockStack", "PropertyValueType"]

class Block(amulet.version.PlatformVersionContainer):
    """
    A class to manage the state of a block.

    It is an immutable object that contains the platform, version, namespace, base name and properties.

    Here's a few examples on how create a Block object:

    >>> # Create a stone block for Java 1.20.2
    >>> stone = Block("java", VersionNumber(3578), "minecraft", "stone")
    >>> # The Java block version number is the Java data version

    >>> # Create a stone block for Bedrock
    >>> stone = Block("bedrock", VersionNumber(1, 21, 0, 3), "minecraft", "stone")
    >>> # The Bedrock block version number is the value stored as an int with the block data.

    >>> # Create a Java water block with the level property
    >>> water = Block(
    >>>     "java", VersionNumber(3578),
    >>>     "minecraft",  # the namespace
    >>>     "water",  # the base name
    >>>     {  # A dictionary of properties.
    >>>         # Keys must be strings and values must be a numerical or string NBT type.
    >>>         "level": StringTag("0")  # define a property `level` with a string value `0`
    >>>     }
    >>> )
    """

    @staticmethod
    def from_bedrock_blockstate(
        platform: str, version: amulet.version.VersionNumber, blockstate: str
    ) -> Block:
        """
        Parse a Bedrock format blockstate where values are all strings and populate a :class:`Block` class with the data.

        >>> stone = Block.from_bedrock_blockstate("minecraft:stone")
        >>> water = Block.from_bedrock_blockstate("minecraft:water["liquid_depth"=0]")

        :param platform: The platform the block is defined in.
        :param version: The version the block is defined in.
        :param blockstate: The Bedrock blockstate string to parse.
        :return: A Block instance containing the state.
        """

    @staticmethod
    def from_java_blockstate(
        platform: str, version: amulet.version.VersionNumber, blockstate: str
    ) -> Block:
        """
        Parse a Java format blockstate where values are all strings and populate a :class:`Block` class with the data.

        >>> stone = Block.from_java_blockstate("minecraft:stone")
        >>> water = Block.from_java_blockstate("minecraft:water[level=0]")

        :param platform: The platform the block is defined in.
        :param version: The version the block is defined in.
        :param blockstate: The Java blockstate string to parse.
        :return: A Block instance containing the state.
        """

    @typing.overload
    def __eq__(self, arg0: Block) -> bool: ...
    @typing.overload
    def __eq__(self, arg0: typing.Any) -> bool | types.NotImplementedType: ...
    def __ge__(self, arg0: Block) -> bool: ...
    def __getstate__(self) -> bytes: ...
    def __gt__(self, arg0: Block) -> bool: ...
    def __hash__(self) -> int: ...
    def __init__(
        self,
        platform: str,
        version: amulet.version.VersionNumber,
        namespace: str,
        base_name: str,
        properties: dict[
            str,
            amulet_nbt.ByteTag
            | amulet_nbt.ShortTag
            | amulet_nbt.IntTag
            | amulet_nbt.LongTag
            | amulet_nbt.StringTag,
        ] = {},
    ) -> None: ...
    def __le__(self, arg0: Block) -> bool: ...
    def __lt__(self, arg0: Block) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, arg0: bytes) -> None: ...
    @property
    def base_name(self) -> str:
        """
        The base name of the blockstate represented by the :class:`Block` object.

        >>> block: Block
        >>> block.base_name

        :return: The base name of the blockstate
        """

    @property
    def bedrock_blockstate(self) -> str:
        """
        The Bedrock blockstate string of this :class:`Block` object.
        Converts the property values to the SNBT format to preserve type.

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
        >>> bell.bedrock_blockstate
        minecraft:bell["attachment"="standing","direction"=0,"toggle_bit"=false]

        :return: The SNBT blockstate string
        """

    @property
    def java_blockstate(self) -> str:
        """
        The Java blockstate string of this :class:`Block` object.
        Note this will only contain properties with StringTag values.

        >>> stone = Block("java", VersionNumber(3578), "minecraft", "stone")
        >>> stone.java_blockstate
        minecraft:stone
        >>> water = Block("java", VersionNumber(3578), "minecraft", "water", {"level": StringTag("0")})
        >>> water.java_blockstate
        minecraft:water[level=0]

        :return: The blockstate string
        """

    @property
    def namespace(self) -> str:
        """
        The namespace of the blockstate represented by the :class:`Block` object.

        >>> block: Block
        >>> water.namespace

        :return: The namespace of the blockstate
        """

    @property
    def namespaced_name(self) -> str:
        """
        The namespace:base_name of the blockstate represented by the :class:`Block` object.

        >>> block: Block
        >>> block.namespaced_name

        :return: The namespace:base_name of the blockstate
        """

    @property
    def properties(
        self,
    ) -> dict[
        str,
        amulet_nbt.ByteTag
        | amulet_nbt.ShortTag
        | amulet_nbt.IntTag
        | amulet_nbt.LongTag
        | amulet_nbt.StringTag,
    ]:
        """
        The properties of the blockstate represented by the :class:`Block` object as a dictionary.
        >>> block: Block
        >>> block.properties

        :return: A mapping of the properties of the blockstate
        """

class BlockStack:
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

    def __contains__(self, arg0: typing.Any) -> bool: ...
    @typing.overload
    def __eq__(self, arg0: BlockStack) -> bool: ...
    @typing.overload
    def __eq__(self, arg0: typing.Any) -> bool | types.NotImplementedType: ...
    def __ge__(self, arg0: BlockStack) -> bool: ...
    @typing.overload
    def __getitem__(self, arg0: int) -> Block: ...
    @typing.overload
    def __getitem__(self, arg0: slice) -> list: ...
    def __gt__(self, arg0: BlockStack) -> bool: ...
    def __hash__(self) -> int: ...
    def __init__(self, block: Block, *extra_blocks: Block) -> None: ...
    def __iter__(self) -> collections.abc.Iterator[Block]: ...
    def __le__(self, arg0: BlockStack) -> bool: ...
    def __len__(self) -> int: ...
    def __lt__(self, arg0: BlockStack) -> bool: ...
    def __repr__(self) -> str: ...
    def __reversed__(self) -> collections.abc.Iterator[Block]: ...
    def count(self, value: typing.Any) -> int: ...
    def index(
        self, value: typing.Any, start: int = 0, stop: int = 9223372036854775807
    ) -> int: ...
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

    @property
    def extra_blocks(self) -> tuple:
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

PropertyValueType: typing.TypeAlias = (
    amulet_nbt.ByteTag
    | amulet_nbt.ShortTag
    | amulet_nbt.IntTag
    | amulet_nbt.LongTag
    | amulet_nbt.StringTag
)
