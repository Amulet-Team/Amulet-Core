from __future__ import annotations

from typing import Union, Iterable, Dict, TYPE_CHECKING, Optional, NamedTuple, Any
import numpy
import pickle

from amulet.block import Block
from amulet.palette import BlockPalette
from amulet.palette import BiomePalette
from amulet.api.chunk import (
    Biomes,
    BiomesShape,
    Blocks,
    Status,
    BlockEntityDict,
    EntityList,
)
from amulet.entity import Entity
from amulet.block_entity import BlockEntity
from amulet.data_types import ChunkCoordinates
from amulet.api.data_types import VersionIdentifierType
from amulet.errors import ChunkLoadError

if TYPE_CHECKING:
    from amulet.level import Level


class _ChunkPickleData(NamedTuple):
    level_id: int
    init_args: tuple[int, int]
    args: dict[str, Any]


class Chunk:
    """
    A class to represent a chunk that exists in a Minecraft world
    """

    def __init__(self, cx: int, cz: int):
        """
        Construct an instance of :class:`Chunk` at the given coordinates.

        :param cx: The x coordinate of the chunk (is not the same as block coordinates)
        :param cz: The z coordinate of the chunk (is not the same as block coordinates)
        """
        super().__init__()
        self._cx: int = cx
        self._cz: int = cz
        self._blocks: Optional[Blocks] = None
        self._block_palette: Optional[BlockPalette] = None
        self._biome_palette: Optional[BiomePalette] = None
        self._biomes: Optional[Biomes] = None
        self._entities: Optional[EntityList] = None
        self._block_entities: Optional[BlockEntityDict] = None
        self._status = Status()
        self._misc = {}  # all entries that are not important enough to get an attribute

        # TODO: remove these variables. They are temporary until the translator supports entities
        self._native_version: VersionIdentifierType = ("java", 0)
        self._native_entities = EntityList()

    def __repr__(self):
        return f"Chunk({self.cx}, {self.cz})"

    def pickle(self, level: Level) -> bytes:
        """
        Serialise the data in the chunk using pickle and return the resulting bytes.
        :param level: The level to serialise against.
        :return: Pickled output.
        """
        if self.block_palette is not level.block_palette:
            self.block_palette = level.block_palette
        if self.biome_palette is not level.biome_palette:
            self.biome_palette = level.biome_palette

        return pickle.dumps(
            _ChunkPickleData(
                id(level),
                (self._cx, self._cz),
                {
                    "_blocks": self._blocks,
                    "_biomes": self._biomes,
                    "_entities": self._entities,
                    "_block_entities": self._block_entities,
                    "_status": self._status,
                    "_misc": self._misc,
                    "_native_version": self._native_version,
                    "_native_entities": self._native_entities,
                },
            )
        )

    @classmethod
    def unpickle(
        cls,
        pickled_bytes: bytes,
        level: Level,
    ) -> Chunk:
        """
        Deserialise the pickled input and unpack the data into an instance of :class:`Chunk`

        :param pickled_bytes: The bytes returned from :func:`pickle`
        :param level: The level to deserialise against.
        :raises:
            :class:`~amulet.errors.ChunkLoadError`: If pickled data was a ChunkLoadError instance.
            RuntimeError if any other case
        :return: An instance of :class:`Chunk` containing the unpickled data.
        """
        chunk_data = pickle.loads(pickled_bytes)
        if isinstance(chunk_data, _ChunkPickleData):
            if id(level) != chunk_data.level_id:
                raise RuntimeError("level is a different level")
            self = cls(*chunk_data.init_args)
            for name, arg in chunk_data.args.items():
                setattr(self, name, arg)
            self._block_palette = level.block_palette
            self._biome_palette = level.biome_palette
            return self
        elif isinstance(chunk_data, ChunkLoadError):
            raise chunk_data
        else:
            raise RuntimeError

    @property
    def cx(self) -> int:
        """The chunk's x coordinate"""
        return self._cx

    @property
    def cz(self) -> int:
        """The chunk's z coordinate"""
        return self._cz

    @property
    def coordinates(self) -> ChunkCoordinates:
        """The chunk's x and z coordinates"""
        return self._cx, self._cz

    @property
    def blocks(self) -> Blocks:
        """
        The block array for the chunk.

        This is a custom class that stores a numpy array per sub-chunk.

        The values in the arrays are indexes into :attr:`block_palette`.
        """
        if self._blocks is None:
            self._blocks = Blocks()
        return self._blocks

    @blocks.setter
    def blocks(self, value: Union[Dict[int, numpy.ndarray], Blocks, None]):
        if isinstance(value, dict):
            value: Dict[int, numpy.ndarray]
            value = {k: v.astype(numpy.uint32) for k, v in value.items()}
        self._blocks = Blocks(value)

    def get_block(self, dx: int, y: int, dz: int) -> Block:
        """
        Get the universal Block object at the given location within the chunk.

        :param dx: The x coordinate within the chunk. 0-15 inclusive
        :param y: The y coordinate within the chunk. This can be any integer.
        :param dz: The z coordinate within the chunk. 0-15 inclusive
        :return: The universal Block object representation of the block at that location
        """
        return self.block_palette.index_to_block(self.blocks[dx, y, dz])

    def set_block(self, dx: int, y: int, dz: int, block: Block):
        """
        Set the universal Block object at the given location within the chunk.

        :param dx: The x coordinate within the chunk. 0-15 inclusive
        :param y: The y coordinate within the chunk. This can be any integer.
        :param dz: The z coordinate within the chunk. 0-15 inclusive
        :param block: The universal Block object to set at the given location
        """
        self.blocks[dx, y, dz] = self.block_palette.block_to_index(block)

    @property
    def block_palette(self) -> BlockPalette:
        """
        The block block_palette for the chunk.

        Usually will refer to the level's global block_palette.
        """
        if self._block_palette is None:
            self._block_palette = BlockPalette()
        return self._block_palette

    @block_palette.setter
    def block_palette(self, new_block_palette: BlockPalette):
        """
        Change the block block_palette for the chunk.

        This will copy over all block states from the old block_palette and remap the block indexes to use the new block_palette.
        """
        assert isinstance(new_block_palette, BlockPalette)
        if new_block_palette is not self._block_palette:
            # if current block block_palette and the new block block_palette are not the same object
            if self._block_palette:
                # if there are blocks in the current block block_palette remap the data
                block_lut = numpy.array(
                    [
                        new_block_palette.block_to_index(block)
                        for block in self._block_palette
                    ],
                    dtype=numpy.uint32,
                )
                for cy in self.blocks.sub_chunks:
                    self.blocks.add_sub_chunk(
                        cy, block_lut[self.blocks.get_sub_chunk(cy)]
                    )

            self._block_palette = new_block_palette

    @property
    def biomes(self) -> Biomes:
        """
        The biome array for the chunk.

        This is a custom class that stores numpy arrays. See the :class:`Biomes` documentation for more information.

        The values in the arrays are indexes into :attr:`biome_palette`.
        """
        if self._biomes is None:
            self._biomes = Biomes()
        return self._biomes

    @biomes.setter
    def biomes(self, value: Union[Biomes, Dict[int, numpy.ndarray]]):
        self._biomes = Biomes(value)

    @property
    def biome_palette(self) -> BiomePalette:
        """
        The biome block_palette for the chunk.

        Usually will refer to the level's global biome_palette.
        """
        if self._biome_palette is None:
            self._biome_palette = BiomePalette()
        return self._biome_palette

    @biome_palette.setter
    def biome_palette(self, new_biome_palette: BiomePalette):
        """
        Change the biome_palette for the chunk.

        This will copy over all biome states from the old biome_palette and remap the biome indexes to use the new_biome_palette.
        """
        assert isinstance(new_biome_palette, BiomePalette)
        if new_biome_palette is not self._biome_palette:
            # if current biome_palette and the new biome_palette are not the same object
            if self._biome_palette:
                # if there are biomes in the current biome_palette remap the data
                biome_lut = numpy.array(
                    [
                        new_biome_palette.biome_to_index(biome)
                        for biome in self._biome_palette
                    ],
                    dtype=numpy.uint32,
                )
                if self.biomes.dimension == BiomesShape.Shape2D:
                    self.biomes = biome_lut[self.biomes]
                elif self.biomes.dimension == BiomesShape.Shape3D:
                    self.biomes = {
                        sy: biome_lut[self.biomes.get_section(sy)]
                        for sy in self.biomes.sections
                    }

            self._biome_palette = new_biome_palette

    @property
    def entities(self) -> EntityList:
        """
        Property that returns the chunk's entity list. Setting this property replaces the chunk's entity list

        :return: A list of all the entities contained in the chunk
        """
        if self._entities is None:
            self._entities = EntityList()
        return self._entities

    @entities.setter
    def entities(self, value: Iterable[Entity]):
        if self._entities != value:
            self._entities = EntityList(value)

    @property
    def block_entities(self) -> BlockEntityDict:
        """
        Property that returns the chunk's block entity list. Setting this property replaces the chunk's block entity list

        :return: A list of all the block entities contained in the chunk
        """
        if self._block_entities is None:
            self._block_entities = BlockEntityDict()
        return self._block_entities

    @block_entities.setter
    def block_entities(self, value: Iterable[BlockEntity]):
        if self._block_entities != value:
            self._block_entities = BlockEntityDict(value)

    @property
    def status(self) -> Status:
        """
        A class containing the chunk's generation status.
        """
        return self._status

    @status.setter
    def status(self, value: Union[float, int, str]):
        self._status.value = value

    @property
    def misc(self) -> dict:
        """
        Extra data that exists in a chunk but does not have its own location.

        Data in here is not guaranteed to exist and may get moved at a later date.
        """
        return self._misc

    @misc.setter
    def misc(self, misc: dict):
        assert isinstance(misc, dict), "misc must be a dictionary."
        self._misc = misc
