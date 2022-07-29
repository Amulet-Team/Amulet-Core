from __future__ import annotations

from sys import getsizeof
import re
from typing import Dict, Iterable, Tuple, Union
from amulet_nbt import ByteTag, ShortTag, IntTag, LongTag, StringTag, from_snbt

from .errors import BlockException

PropertyValueType = Union[
    ByteTag,
    ShortTag,
    IntTag,
    LongTag,
    StringTag,
]
PropertyType = Dict[str, PropertyValueType]
PropertyTypeMultiple = Dict[str, Tuple[PropertyValueType, ...]]

PropertyDataTypes = (
    ByteTag,
    ShortTag,
    IntTag,
    LongTag,
    StringTag,
)


class Block:
    """
    A class to manage the state of a block.

    It is an immutable object that contains a namespaced name, properties and extra blocks.

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

    Java 1.13 added the concept of waterlogging blocks whereby some blocks have a `waterlogged` property.
    Bedrock achieved the same behaviour by added a layering system. The layering system allows any block to be the second block.
    In order to support both formats and future proof the editor Amulet adds the concept of extra blocks.
    Extra blocks are a sequence of zero or more blocks stored in the `extra_blocks` property of the Block instance.
    Amulet places no restrictions on which blocks can be extra blocks but some validation will be done when saving based on the format being saved to.

    >>> # Create a waterlogged stone block.
    >>> waterlogged_stone = Block("minecraft", "stone",
    >>>     # extra_blocks can be a Block instance or iterable of Block instances.
    >>>     extra_blocks=Block("minecraft", "water", {"level": StringTag("0")})
    >>> )

    >>> # The above can also be achieved by adding together a stone and water block.
    >>> waterlogged_stone = stone + water
    >>> repr(waterlogged_stone)
    'Block(minecraft:stone, extra_blocks=(minecraft:water[level="0"]))'
    """

    __slots__ = (
        "_namespaced_name",
        "_namespace",
        "_base_name",
        "_properties",
        "_extra_blocks",
        "_blockstate",
        "_snbt_blockstate",
        "_full_blockstate",
    )  # Reduces memory footprint

    snbt_blockstate_regex = re.compile(
        r"(?:(?P<namespace>[a-z0-9_.-]+):)?(?P<base_name>[a-z0-9/._-]+)(?:\[(?P<property_name>[a-z0-9_]+)=(?P<property_value>[a-z0-9_\"']+)(?P<properties>.*)\])?"
    )
    blockstate_regex = re.compile(
        r"(?:(?P<namespace>[a-z0-9_.-]+):)?(?P<base_name>[a-z0-9/._-]+)(?:\[(?P<property_name>[a-z0-9_]+)=(?P<property_value>[a-z0-9_]+)(?P<properties>.*)\])?"
    )

    snbt_properties_regex = re.compile(
        r"(?:,(?P<name>[a-z0-9_]+)=(?P<value>[a-z0-9_\"']+))"
    )
    properties_regex = re.compile(r"(?:,(?P<name>[a-z0-9_]+)=(?P<value>[a-z0-9_]+))")

    _extra_blocks: Tuple[Block, ...]

    def __init__(
        self,
        namespace: str,
        base_name: str,
        properties: PropertyType = None,
        extra_blocks: Union[Block, Iterable[Block]] = None,
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
        :param properties: A dictionary of properties. Keys must be strings and values must be a numerical or string NBT type.
        :param extra_blocks: A :class:`Block` instance or iterable of :class:`Block` instances
        """
        assert (isinstance(namespace, str) or namespace is None) and isinstance(
            base_name, str
        ), f"namespace and base_name must be strings {namespace} {base_name}"
        self._namespace = namespace
        self._base_name = base_name
        self._namespaced_name = f"{namespace}:{base_name}"

        self._blockstate = None
        self._snbt_blockstate = None
        self._full_blockstate = None

        if properties is None:
            properties = {}
        assert isinstance(properties, dict) and all(
            isinstance(val, PropertyDataTypes) for val in properties.values()
        ), properties

        self._properties = properties
        self._extra_blocks = ()
        if extra_blocks:
            eb = []

            def unpack_block(block_: Iterable[Block]):
                for b in block_:
                    if b.extra_blocks:
                        unpack_block(b)
                    else:
                        eb.append(b)

            unpack_block(extra_blocks)
            self._extra_blocks = tuple(eb)

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

    @property
    def namespaced_name(self) -> str:
        """
        The namespace:base_name of the blockstate represented by the :class:`Block` object.

        >>> water = Block.from_string_blockstate("minecraft:water[level=0]")
        >>> water.namespaced_name
        'minecraft:water'

        :return: The namespace:base_name of the blockstate
        """
        return self._namespaced_name

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
    def properties(self) -> PropertyType:
        """
        The mapping of properties of the blockstate represented by the :class:`Block` object.

        >>> water = Block.from_string_blockstate("minecraft:water[level=0]")
        >>> water.properties
        {"level": StringTag("0")}

        :return: A dictionary of the properties of the blockstate
        """
        return dict(self._properties)

    @property
    def blockstate(self) -> str:
        """
        The Java blockstate string of this :class:`Block` object
        Note if there are extra blocks this will only show the base block.
        Note this will only contain properties with StringTag values.

        >>> stone = Block("minecraft", "stone")
        >>> stone.blockstate
        'minecraft:stone'
        >>> water = Block("minecraft", "water", {"level": StringTag("0")})
        >>> water.blockstate
        `minecraft:water[level=0]`

        :return: The blockstate string
        """
        if self._blockstate is None:
            self._blockstate = self.namespaced_name
            if self.properties:
                props = [
                    f"{key}={value.py_str}"
                    for key, value in sorted(self.properties.items())
                    if isinstance(value, StringTag)
                ]
                self._blockstate += f"[{','.join(props)}]"
        return self._blockstate

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
        if self._snbt_blockstate is None:
            self._snbt_blockstate = self.namespaced_name
            if self.properties:
                props = [
                    f"{key}={value.to_snbt()}"
                    for key, value in sorted(self.properties.items())
                ]
                self._snbt_blockstate += f"[{','.join(props)}]"
        return self._snbt_blockstate

    @property
    def full_blockstate(self) -> str:
        """
        The SNBT blockstate string of the base block and extra blocks.

        >>> bell = Block("minecraft", "bell", {
        >>>     "attachment":StringTag("standing"),
        >>>     "direction":IntTag(0),
        >>>     "toggle_bit":ByteTag(0)
        >>> })
        >>> water = Block("minecraft", "water", {"liquid_depth": IntTag(0)})
        >>> waterlogged_bell = bell + water
        >>> waterlogged_bell.full_blockstate
        'minecraft:bell[attachment="standing",direction=0,toggle_bit=0b]{minecraft:water[liquid_depth=0]}'

        :return: The blockstate string
        """
        if self._full_blockstate is None:
            if self.extra_blocks:
                self._full_blockstate = f"{self.snbt_blockstate}{{{' , '.join(block.snbt_blockstate for block in self.extra_blocks)}}}"
            else:
                self._full_blockstate = self.snbt_blockstate
        return self._full_blockstate

    @property
    def base_block(self) -> Block:
        """
        Returns an instance of :class:`Block` containing only the base block without any extra blocks

        >>> waterlogged_stone = Block("minecraft", "stone",
        >>>     extra_blocks=Block("minecraft", "water", {"level": StringTag("0")})
        >>> )
        >>> waterlogged_stone.base_block
        Block(minecraft:stone)

        :return: A Block object
        """
        if self.extra_blocks:
            return Block(
                namespace=self.namespace,
                base_name=self.base_name,
                properties=self.properties,
            )
        else:
            return self

    @property
    def extra_blocks(self) -> Tuple[Block, ...]:
        """
        Returns a tuple of the extra blocks contained in the :class:`Block` instance

        >>> waterlogged_stone = Block("minecraft", "stone",
        >>>     extra_blocks=Block("minecraft", "water", {"level": StringTag("0")})
        >>> )
        >>> waterlogged_stone.extra_blocks
        (Block(minecraft:water[level="0"]),)

        :return: A tuple of :class:`Block` objects
        """
        return self._extra_blocks

    @property
    def block_tuple(self) -> Tuple[Block, ...]:
        """
        Returns the stack of blocks represented by this object as a tuple.
        This is a tuple of base_block and extra_blocks

        >>> waterlogged_stone = Block("minecraft", "stone",
        >>>     extra_blocks=Block("minecraft", "water", {"level": StringTag("0")})
        >>> )
        >>> waterlogged_stone.block_tuple
        (Block(minecraft:stone), Block(minecraft:water[level="0"]))

        :return: A tuple of :class:`Block` objects
        """
        return (self.base_block,) + self.extra_blocks

    @staticmethod
    def parse_blockstate_string(
        blockstate: str, snbt: bool = False
    ) -> Tuple[str, str, PropertyType]:
        """
        Parse a Java or SNBT blockstate string and return the raw data.

        To parse the blockstate and return a :class:`Block` instance use :func:`from_string_blockstate` or :func:`from_snbt_blockstate`

        :param blockstate: The blockstate to parse
        :param snbt: Are the property values in SNBT format. If false all values must be an instance of :class:`~StringTag`
        :return: namespace, block_name, properties

        """
        if snbt:
            match = Block.snbt_blockstate_regex.match(blockstate)
        else:
            match = Block.blockstate_regex.match(blockstate)
        namespace = match.group("namespace") or "minecraft"
        base_name = match.group("base_name")

        if match.group("property_name") is not None:
            properties = {match.group("property_name"): match.group("property_value")}
            properties_string = match.group("properties")
            if properties_string is not None:
                if snbt:
                    for match in Block.snbt_properties_regex.finditer(
                        properties_string
                    ):
                        properties[match.group("name")] = match.group("value")
                else:
                    for match in Block.properties_regex.finditer(properties_string):
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

    def __str__(self) -> str:
        """

        >>> waterlogged_stone = Block("minecraft", "stone",
        >>>     extra_blocks=Block("minecraft", "water", {"level": StringTag("0")})
        >>> )
        >>> str(waterlogged_stone)
        'minecraft:stone{minecraft:water[level="0"]}'

        :return: A string showing the information of the :class:`Block` class.
        """
        return self.full_blockstate

    def __repr__(self) -> str:
        """

        >>> waterlogged_stone = Block("minecraft", "stone",
        >>>     extra_blocks=Block("minecraft", "water", {"level": StringTag("0")})
        >>> )
        >>> repr(waterlogged_stone)
        'Block(minecraft:stone, extra_blocks=(minecraft:water[level="0"]))'

        :return: The base blockstate string of the Block object along with the blockstate strings of included extra blocks
        """
        if self.extra_blocks:
            return f"Block({self.base_block}, extra_blocks=({', '.join([str(b) for b in self.extra_blocks])}))"
        else:
            return f"Block({self.base_block})"

    def __iter__(self) -> Iterable[Block]:
        """
        Iterate through all the blocks in this :class:`Block` instance.

        >>> waterlogged_stone = Block("minecraft", "stone",
        >>>     extra_blocks=Block("minecraft", "water", {"level": StringTag("0")})
        >>> )
        >>> for block in waterlogged_stone:
        >>>     print(block)
        minecraft:stone
        minecraft:water[level="0"]
        """
        yield self.base_block
        yield from self.extra_blocks

    def __len__(self) -> int:
        """
        The number of blocks contained within the :class:`Block` instance.

        >>> waterlogged_stone = Block("minecraft", "stone",
        >>>     extra_blocks=Block("minecraft", "water", {"level": StringTag("0")})
        >>> )
        >>> len(waterlogged_stone)
        2
        """
        return len(self._extra_blocks) + 1

    def __eq__(self, other: Block) -> bool:
        """
        Checks the equality of this Block object to another Block object

        >>> stone = Block("minecraft", "stone")
        >>> stone == stone
        True

        :param other: The Block object to check against
        :return: True if the Blocks objects are equal, False otherwise
        """
        if not isinstance(other, Block):
            return NotImplemented

        return (
            self.namespaced_name == other.namespaced_name
            and self.properties == other.properties
            and self.extra_blocks == other.extra_blocks
        )

    def __gt__(self, other: Block) -> bool:
        """
        Allows blocks to be sorted so numpy.unique can be used on them
        """
        if not isinstance(other, Block):
            return NotImplemented
        return hash(self).__gt__(hash(other))

    def __hash__(self) -> int:
        """
        Hashes the Block object

        :return: A hash of the Block object
        """
        return hash(self.full_blockstate)

    def __add__(self, other: Block) -> Block:
        """
        Add the blocks from `other` to this block.

        >>> stone = Block("minecraft", "stone")
        >>> water = Block("minecraft", "water", {"level": StringTag("0")})
        >>> waterlogged_stone = stone + water
        >>> repr(waterlogged_stone)
        'Block(minecraft:stone, extra_blocks=(minecraft:water[level="0"]))'

        :param other: The :class:`Block` object to add to this :class:`Block`
        :return: A new instance of :class:`Block` with the blocks from other appended to the end of :attr:`extra_blocks`
        """
        if not isinstance(other, Block):
            return NotImplemented

        return Block(
            namespace=self.namespace,
            base_name=self.base_name,
            properties=self.properties,
            extra_blocks=[*self.extra_blocks, other],
        )

    def __sub__(self, other: Block) -> Block:
        """
        Remove all blocks in `other` from the :attr:`extra_blocks` of this instance of :class:`Block`

        >>> stone = Block("minecraft", "stone")
        >>> water = Block("minecraft", "water", {"level": StringTag("0")})
        >>> waterlogged_stone = stone + water
        >>> stone = waterlogged_stone - water

        :param other: The Block object to subtract from this :class:`Block`.
        :return: A new :class:`Block` instance with the blocks in `other` removed from the extra blocks.
        """
        if not isinstance(other, Block):
            return NotImplemented

        extra_blocks_to_remove = set(other)
        new_extras = tuple(
            eb for eb in self.extra_blocks if eb not in extra_blocks_to_remove
        )

        return Block(
            namespace=self.namespace,
            base_name=self.base_name,
            properties=self.properties,
            extra_blocks=new_extras,
        )

    def remove_layer(self, layer: int) -> Block:
        """
        Removes the block at the given index and returns the resulting new Block object.

        >>> stone = Block("minecraft", "stone")
        >>> water = Block("minecraft", "water", {"level": StringTag("0")})
        >>> waterlogged_stone = stone + water
        >>> stone = waterlogged_stone.remove_layer(1)

        :param layer: The layer of extra block to remove.
        :return: A new instance of Block with the same data but with the block at the specified layer removed.
        :raises `BlockException`: Raised when you remove the base block from a Block with no other extra blocks.
        """
        if layer == 0:
            if self.extra_blocks:
                new_base = self._extra_blocks[0]
                return Block(
                    namespace=new_base.namespace,
                    base_name=new_base.base_name,
                    properties=new_base.properties,
                    extra_blocks=[*self._extra_blocks[1:]],
                )
            else:
                raise BlockException(
                    "Removing the base block with no extra blocks is not supported"
                )
        elif layer > len(self.extra_blocks):
            raise BlockException("You cannot remove a non-existent layer")
        else:
            return Block(
                namespace=self.namespace,
                base_name=self.base_name,
                properties=self.properties,
                extra_blocks=[
                    *self.extra_blocks[: layer - 1],
                    *self.extra_blocks[layer:],
                ],
            )

    def __sizeof__(self):
        size = (
            getsizeof(self._namespace)
            + getsizeof(self._base_name)
            + getsizeof(self._namespaced_name)
            + getsizeof(self._properties)
            + getsizeof(self._blockstate)
            + getsizeof(self._extra_blocks)
            + getsizeof(self._snbt_blockstate)
            + getsizeof(self._full_blockstate)
        )
        for eb in self.extra_blocks:
            size += getsizeof(eb)
        return size


# some blocks that probably will not change. Keeping these in one place will make them easier to change if they do.
UniversalAirBlock = Block("universal_minecraft", "air")
# do not rely on this staying the same.
UniversalAirLikeBlocks = (UniversalAirBlock, Block("universal_minecraft", "cave_air"))
