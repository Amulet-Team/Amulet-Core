import numpy
from _typeshed import Incomplete
from amulet.api.chunk import Biomes as Biomes, BiomesShape as BiomesShape, BlockEntityDict as BlockEntityDict, Blocks as Blocks, EntityList as EntityList, Status as Status
from amulet.api.data_types import ChunkCoordinates as ChunkCoordinates, VersionIdentifierType as VersionIdentifierType
from amulet.api.errors import ChunkLoadError as ChunkLoadError
from amulet.block import Block as Block
from amulet.block_entity import BlockEntity as BlockEntity
from amulet.entity import Entity as Entity
from amulet.level import Level as Level
from amulet.palette import BiomePalette as BiomePalette, BlockPalette as BlockPalette
from typing import Any, Dict, Iterable, NamedTuple, Union

class _ChunkPickleData(NamedTuple):
    level_id: int
    init_args: tuple[int, int]
    args: dict[str, Any]

class Chunk:
    """
    A class to represent a chunk that exists in a Minecraft world
    """
    _cx: Incomplete
    _cz: Incomplete
    _blocks: Incomplete
    _block_palette: Incomplete
    _biome_palette: Incomplete
    _biomes: Incomplete
    _entities: Incomplete
    _block_entities: Incomplete
    _status: Incomplete
    _misc: Incomplete
    _native_version: Incomplete
    _native_entities: Incomplete
    def __init__(self, cx: int, cz: int) -> None:
        """
        Construct an instance of :class:`Chunk` at the given coordinates.

        :param cx: The x coordinate of the chunk (is not the same as block coordinates)
        :param cz: The z coordinate of the chunk (is not the same as block coordinates)
        """
    def __repr__(self) -> str: ...
    def pickle(self, level: Level) -> bytes:
        """
        Serialise the data in the chunk using pickle and return the resulting bytes.
        :param level: The level to serialise against.
        :return: Pickled output.
        """
    @classmethod
    def unpickle(cls, pickled_bytes: bytes, level: Level) -> Chunk:
        """
        Deserialise the pickled input and unpack the data into an instance of :class:`Chunk`

        :param pickled_bytes: The bytes returned from :func:`pickle`
        :param level: The level to deserialise against.
        :raises:
            :class:`~amulet.api.errors.ChunkLoadError`: If pickled data was a ChunkLoadError instance.
            RuntimeError if any other case
        :return: An instance of :class:`Chunk` containing the unpickled data.
        """
    @property
    def cx(self) -> int:
        """The chunk's x coordinate"""
    @property
    def cz(self) -> int:
        """The chunk's z coordinate"""
    @property
    def coordinates(self) -> ChunkCoordinates:
        """The chunk's x and z coordinates"""
    @property
    def blocks(self) -> Blocks:
        """
        The block array for the chunk.

        This is a custom class that stores a numpy array per sub-chunk.

        The values in the arrays are indexes into :attr:`block_palette`.
        """
    @blocks.setter
    def blocks(self, value: Union[Dict[int, numpy.ndarray], Blocks, None]): ...
    def get_block(self, dx: int, y: int, dz: int) -> Block:
        """
        Get the universal Block object at the given location within the chunk.

        :param dx: The x coordinate within the chunk. 0-15 inclusive
        :param y: The y coordinate within the chunk. This can be any integer.
        :param dz: The z coordinate within the chunk. 0-15 inclusive
        :return: The universal Block object representation of the block at that location
        """
    def set_block(self, dx: int, y: int, dz: int, block: Block):
        """
        Set the universal Block object at the given location within the chunk.

        :param dx: The x coordinate within the chunk. 0-15 inclusive
        :param y: The y coordinate within the chunk. This can be any integer.
        :param dz: The z coordinate within the chunk. 0-15 inclusive
        :param block: The universal Block object to set at the given location
        """
    @property
    def block_palette(self) -> BlockPalette:
        """
        The block block_palette for the chunk.

        Usually will refer to the level's global block_palette.
        """
    @block_palette.setter
    def block_palette(self, new_block_palette: BlockPalette):
        """
        Change the block block_palette for the chunk.

        This will copy over all block states from the old block_palette and remap the block indexes to use the new block_palette.
        """
    @property
    def biomes(self) -> Biomes:
        """
        The biome array for the chunk.

        This is a custom class that stores numpy arrays. See the :class:`Biomes` documentation for more information.

        The values in the arrays are indexes into :attr:`biome_palette`.
        """
    @biomes.setter
    def biomes(self, value: Union[Biomes, Dict[int, numpy.ndarray]]): ...
    @property
    def biome_palette(self) -> BiomePalette:
        """
        The biome block_palette for the chunk.

        Usually will refer to the level's global biome_palette.
        """
    @biome_palette.setter
    def biome_palette(self, new_biome_palette: BiomePalette):
        """
        Change the biome_palette for the chunk.

        This will copy over all biome states from the old biome_palette and remap the biome indexes to use the new_biome_palette.
        """
    @property
    def entities(self) -> EntityList:
        """
        Property that returns the chunk's entity list. Setting this property replaces the chunk's entity list

        :return: A list of all the entities contained in the chunk
        """
    @entities.setter
    def entities(self, value: Iterable[Entity]): ...
    @property
    def block_entities(self) -> BlockEntityDict:
        """
        Property that returns the chunk's block entity list. Setting this property replaces the chunk's block entity list

        :return: A list of all the block entities contained in the chunk
        """
    @block_entities.setter
    def block_entities(self, value: Iterable[BlockEntity]): ...
    @property
    def status(self) -> Status:
        """
        A class containing the chunk's generation status.
        """
    @status.setter
    def status(self, value: Union[float, int, str]): ...
    @property
    def misc(self) -> dict:
        """
        Extra data that exists in a chunk but does not have its own location.

        Data in here is not guaranteed to exist and may get moved at a later date.
        """
    @misc.setter
    def misc(self, misc: dict): ...
