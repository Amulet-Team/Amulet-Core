from _typeshed import Incomplete
from amulet.version import AbstractVersion as AbstractVersion, DataVersion as DataVersion, VersionContainer as VersionContainer
from amulet_nbt import ByteTag, IntTag, LongTag, ShortTag, StringTag
from collections.abc import Hashable, Iterator, Mapping, Sequence
from typing import Union

PropertyValueType = Union[ByteTag, ShortTag, IntTag, LongTag, StringTag]
PropertyType = Mapping[str, PropertyValueType]
PropertyTypeMultiple = dict[str, tuple[PropertyValueType, ...]]
PropertyDataTypes: Incomplete
_BlockstatePattern: Incomplete
_PropertiesPattern: Incomplete
_SNBTPropertiesPattern: Incomplete

class BlockProperties(Mapping[str, PropertyValueType], Hashable):
    """An immutable and hashable mapping from strings to nbt objects."""
    _properties: Incomplete
    _hash: Incomplete
    def __init__(self, properties: Mapping[str, PropertyValueType]) -> None: ...
    def __getitem__(self, key: str) -> PropertyValueType: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[str]: ...
    def __hash__(self) -> int: ...

class Block(VersionContainer):
    '''
    A class to manage the state of a block.

    It is an immutable object that contains a namespace, base name and properties and optionally a version.

    Here\'s a few examples on how create a Block object:

    >>> # Create a block with the namespace `minecraft` and base name `stone`
    >>> stone = Block(DataVersion("java", 3578), "minecraft", "stone")

    >>> # Create a water block with the level property
    >>> water = Block(
    >>>     DataVersion("java", 3578),
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
    '''
    __slots__: Incomplete
    _namespace: Incomplete
    _base_name: Incomplete
    _properties: Incomplete
    def __init__(self, version: AbstractVersion, namespace: str, base_name: str, properties: PropertyType = ...) -> None:
        '''
        Constructs a :class:`Block` instance.

        >>> stone = Block(DataVersion("java", 3578), "minecraft", "stone")
        >>>
        >>> # Create a water block with the level property
        >>> water = Block(
        >>>     DataVersion("java", 3578),
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
        '''
    @classmethod
    def from_string_blockstate(cls, version: AbstractVersion, blockstate: str):
        '''
        Parse a Java format blockstate where values are all strings and populate a :class:`Block` class with the data.

        >>> stone = Block.from_string_blockstate("minecraft:stone")
        >>> water = Block.from_string_blockstate("minecraft:water[level=0]")

        :param version: The version the block is defined in.
        :param blockstate: The Java blockstate string to parse.
        :return: A Block instance containing the state.
        '''
    @classmethod
    def from_snbt_blockstate(cls, version: AbstractVersion, blockstate: str):
        """
        Parse a blockstate where values are SNBT of any type and populate a :class:`Block` class with the data.
        """
    @staticmethod
    def _parse_blockstate_string(blockstate: str, snbt: bool = ...) -> tuple[str, str, PropertyType]:
        """
        Parse a Java or SNBT blockstate string and return the raw data.

        To parse the blockstate and return a :class:`Block` instance use :func:`from_string_blockstate` or :func:`from_snbt_blockstate`

        :param blockstate: The blockstate to parse
        :param snbt: Are the property values in SNBT format. If false all values must be an instance of :class:`~StringTag`
        :return: namespace, block_name, properties

        """
    def _data(self): ...
    def __hash__(self): ...
    def __eq__(self, other): ...
    def __gt__(self, other): ...
    def __lt__(self, other): ...
    def __repr__(self) -> str: ...
    @property
    def namespaced_name(self) -> str:
        '''
        The namespace:base_name of the blockstate represented by the :class:`Block` object.

        >>> water = Block.from_string_blockstate("minecraft:water[level=0]")
        >>> water.namespaced_name
        \'minecraft:water\'

        :return: The namespace:base_name of the blockstate
        '''
    @property
    def namespace(self) -> str:
        '''
        The namespace of the blockstate represented by the :class:`Block` object.

        >>> water = Block.from_string_blockstate("minecraft:water[level=0]")
        >>> water.namespace
        \'minecraft\'

        :return: The namespace of the blockstate
        '''
    @property
    def base_name(self) -> str:
        '''
        The base name of the blockstate represented by the :class:`Block` object.

        >>> water = Block.from_string_blockstate("minecraft:water[level=0]")
        >>> water.base_name
        \'water\'

        :return: The base name of the blockstate
        '''
    @property
    def properties(self) -> BlockProperties:
        '''
        The mapping of properties of the blockstate represented by the :class:`Block` object.
        >>> water = Block.from_string_blockstate("minecraft:water[level=0]")
        >>> water.properties
        {"level": StringTag("0")}
        :return: A mapping of the properties of the blockstate
        '''
    @property
    def blockstate(self) -> str:
        '''
        The Java blockstate string of this :class:`Block` object
        Note this will only contain properties with StringTag values.

        >>> stone = Block(DataVersion("java", 3578), "minecraft", "stone")
        >>> stone.blockstate
        \'minecraft:stone\'
        >>> water = Block(DataVersion("java", 3578), "minecraft", "water", {"level": StringTag("0")})
        >>> water.blockstate
        `minecraft:water[level=0]`

        :return: The blockstate string
        '''
    @property
    def snbt_blockstate(self) -> str:
        '''
        A modified version of the Java blockstate format that supports all NBT types.
        Converts the property values to the SNBT format to preserve type.
        Note if there are extra blocks this will only show the base block.

        >>> bell = Block(
        >>>     DataVersion("java", 3578),
        >>>     "minecraft",
        >>>     "bell",
        >>>     {
        >>>         "attachment":StringTag("standing"),
        >>>         "direction":IntTag(0),
        >>>         "toggle_bit":ByteTag(0)
        >>>     }
        >>> )
        >>> bell.snbt_blockstate
        \'minecraft:bell[attachment="standing",direction=0,toggle_bit=0b]\'

        :return: The SNBT blockstate string
        '''

class BlockStack(Sequence[Block]):
    '''
    A stack of block objects.

    Java 1.13 added the concept of waterlogging blocks whereby some blocks have a `waterlogged` property.
    Bedrock achieved the same behaviour by added a layering system which allows the second block to be any block.

    Amulet supports both implementations with a stack of one or more block objects similar to how Bedrock handles it.
    Amulet places no restrictions on which blocks can be extra blocks.
    Extra block may be discarded if the format does not support them.

    Create a waterlogged stone block.
    >>> waterlogged_stone = BlockStack(
    >>>     Block(DataVersion("java", 3578), "minecraft", "stone"),
    >>>     Block(DataVersion("java", 3578), "minecraft", "water", {"level": StringTag("0")})
    >>> )

    Get a block at an index
    >>> stone = waterlogged_stone[0]
    >>> water = waterlogged_stone[1]

    Get the blocks as a list
    >>> blocks = list(waterlogged_stone)
    '''
    __slots__: Incomplete
    _blocks: Incomplete
    def __init__(self, block: Block, *extra_blocks: Block) -> None: ...
    def __repr__(self) -> str: ...
    def __len__(self) -> int: ...
    def __getitem__(self, item): ...
    def __hash__(self): ...
    def __eq__(self, other): ...
    @property
    def base_block(self) -> Block:
        '''
        The first block in the stack.

        >>> waterlogged_stone = BlockStack(
        >>>     Block(DataVersion("java", 3578), "minecraft", "stone"),
        >>>     Block(DataVersion("java", 3578), "minecraft", "water", {"level": StringTag("0")})
        >>> )
        >>> waterlogged_stone.base_block
        Block(DataVersion("java", 3578), "minecraft", "stone")

        :return: A Block object
        '''
    @property
    def extra_blocks(self) -> tuple[Block, ...]:
        '''
        The extra blocks in the stack.

        >>> waterlogged_stone = BlockStack(
        >>>     Block(DataVersion("java", 3578), "minecraft", "stone"),
        >>>     Block(DataVersion("java", 3578), "minecraft", "water", {"level": StringTag("0")})
        >>> )
        >>> waterlogged_stone.extra_blocks
        (Block(DataVersion("java", 3578), "minecraft", "water", {"level": StringTag("0")}),)

        :return: A tuple of :class:`Block` objects
        '''
