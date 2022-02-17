from __future__ import annotations

from typing import Union, Iterable, Dict
import time
import numpy
import pickle

from amulet.api.block import Block
from amulet.api.registry import BlockManager
from amulet.api.registry.biome_manager import BiomeManager
from amulet.api.chunk import (
    Biomes,
    BiomesShape,
    Blocks,
    Status,
    BlockEntityDict,
    EntityList,
)
from amulet.api.entity import Entity
from amulet.api.data_types import ChunkCoordinates, VersionIdentifierType
from amulet.api.history.changeable import Changeable


class Chunk(Changeable):
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
        self._cx, self._cz = cx, cz
        self._changed_time = 0.0

        self._blocks = None
        self.__block_palette = BlockManager()
        self.__biome_palette = BiomeManager()
        self._biomes = None
        self._entities = EntityList()
        self._block_entities = BlockEntityDict()
        self._status = Status()
        self._misc = {}  # all entries that are not important enough to get an attribute

        # TODO: remove these variables. They are temporary until the translator supports entities
        self._native_version: VersionIdentifierType = ("java", 0)
        self._native_entities = EntityList()

    def __repr__(self):
        return f"Chunk({self.cx}, {self.cz}, {repr(self._blocks)}, {repr(self._entities)}, {repr(self._block_entities)})"

    def pickle(self) -> bytes:
        """
        Serialise the data in the chunk using pickle and return the resulting bytes.

        :return: Pickled output.
        """
        chunk_data = (
            self._cx,
            self._cz,
            self._changed_time,
            {sy: self.blocks.get_sub_chunk(sy) for sy in self.blocks.sub_chunks},
            self.biomes.to_raw(),
            self._entities.data,
            tuple(self._block_entities.data.values()),
            self._status.value,
            self.misc,
            self._native_entities,
            self._native_version,
        )
        return pickle.dumps(chunk_data)

    @classmethod
    def unpickle(
        cls,
        pickled_bytes: bytes,
        block_palette: BlockManager,
        biome_palette: BiomeManager,
    ) -> Chunk:
        """
        Deserialise the pickled input and unpack the data into an instance of :class:`Chunk`

        :param pickled_bytes: The bytes returned from :func:`pickle`
        :param block_palette: The instance of :class:`BlockManager` associated with the level.
        :param biome_palette: The instance of :class:`BiomeManager` associated with the level.
        :return: An instance of :class:`Chunk` containing the unpickled data.
        """
        chunk_data = pickle.loads(pickled_bytes)
        self = cls(*chunk_data[:2])
        (
            self.blocks,
            biomes,
            self.entities,
            self.block_entities,
            self.status,
            self.misc,
            self._native_entities,
            self._native_version,
        ) = chunk_data[3:]

        self._biomes = Biomes.from_raw(*biomes)

        self._changed_time = chunk_data[2]
        self._block_palette = block_palette
        self._biome_palette = biome_palette
        self.changed = False
        return self

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
    def changed(self) -> bool:
        """
        Has the chunk changed since the last undo point. Is used to track which chunks have changed.

        >>> chunk = Chunk(0, 0)
        >>> # Run this to notify that the chunk data has changed.
        >>> chunk.changed = True

        :setter: Set this to ``True`` if you have modified the chunk in any way.
        :return: ``True`` if the chunk has been changed since the last undo point, ``False`` otherwise.
        """
        return self._changed

    @changed.setter
    def changed(self, changed: bool):
        assert isinstance(changed, bool), "Changed value must be a bool"
        self._changed = changed
        if changed:
            self._changed_time = time.time()

    @property
    def changed_time(self) -> float:
        """
        The last time the chunk was changed

        Used to track if the chunk was changed since the last save snapshot and if the chunk model needs rebuilding.
        """
        return self._changed_time

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
        return self.block_palette[self.blocks[dx, y, dz]]

    def set_block(self, dx: int, y: int, dz: int, block: Block):
        """
        Set the universal Block object at the given location within the chunk.

        :param dx: The x coordinate within the chunk. 0-15 inclusive
        :param y: The y coordinate within the chunk. This can be any integer.
        :param dz: The z coordinate within the chunk. 0-15 inclusive
        :param block: The universal Block object to set at the given location
        """
        self.blocks[dx, y, dz] = self.block_palette.get_add_block(block)

    @property
    def _block_palette(self) -> BlockManager:
        """The block block_palette for the chunk.
        Usually will refer to a global block block_palette."""
        return self.__block_palette

    @_block_palette.setter
    def _block_palette(self, new_block_palette: BlockManager):
        """Change the block block_palette for the chunk.
        This will change the block block_palette but leave the block array unchanged.
        Only use this if you know what you are doing.
        Designed for internal use. You probably want to use Chunk.block_palette"""
        assert isinstance(new_block_palette, BlockManager)
        self.__block_palette = new_block_palette

    @property
    def block_palette(self) -> BlockManager:
        """
        The block block_palette for the chunk.

        Usually will refer to the level's global block_palette.
        """
        return self._block_palette

    @block_palette.setter
    def block_palette(self, new_block_palette: BlockManager):
        """
        Change the block block_palette for the chunk.

        This will copy over all block states from the old block_palette and remap the block indexes to use the new block_palette.
        """
        assert isinstance(new_block_palette, BlockManager)
        if new_block_palette is not self._block_palette:
            # if current block block_palette and the new block block_palette are not the same object
            if self._block_palette:
                # if there are blocks in the current block block_palette remap the data
                block_lut = numpy.array(
                    [
                        new_block_palette.get_add_block(block)
                        for block in self._block_palette.blocks
                    ],
                    dtype=numpy.uint32,
                )
                for cy in self.blocks.sub_chunks:
                    self.blocks.add_sub_chunk(
                        cy, block_lut[self.blocks.get_sub_chunk(cy)]
                    )

            self.__block_palette = new_block_palette

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
    def _biome_palette(self) -> BiomeManager:
        """
        The biome_palette for the chunk.

        Usually will refer to a global biome_palette.
        """
        return self.__biome_palette

    @_biome_palette.setter
    def _biome_palette(self, new_biome_palette: BiomeManager):
        """
        Change the biome_palette for the chunk.

        This will change the biome_palette but leave the biome array unchanged.

        Only use this if you know what you are doing.

        Designed for internal use. You probably want to use Chunk.biome_palette
        """
        assert isinstance(new_biome_palette, BiomeManager)
        self.__biome_palette = new_biome_palette

    @property
    def biome_palette(self) -> BiomeManager:
        """
        The biome block_palette for the chunk.

        Usually will refer to the level's global biome_palette.
        """
        return self._biome_palette

    @biome_palette.setter
    def biome_palette(self, new_biome_palette: BiomeManager):
        """
        Change the biome_palette for the chunk.

        This will copy over all biome states from the old biome_palette and remap the biome indexes to use the new_biome_palette.
        """
        assert isinstance(new_biome_palette, BiomeManager)
        if new_biome_palette is not self._biome_palette:
            # if current biome_palette and the new biome_palette are not the same object
            if self._biome_palette:
                # if there are biomes in the current biome_palette remap the data
                biome_lut = numpy.array(
                    [
                        new_biome_palette.get_add_biome(biome)
                        for biome in self._biome_palette.biomes
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

            self.__biome_palette = new_biome_palette

    @property
    def entities(self) -> EntityList:
        """
        Property that returns the chunk's entity list. Setting this property replaces the chunk's entity list

        :return: A list of all the entities contained in the chunk
        """
        return self._entities

    @entities.setter
    def entities(self, value: Iterable[Entity]):
        """
        :param value: The new entity list
        :type value: list
        :return:
        """
        if self._entities != value:
            self._entities = EntityList(value)

    @property
    def block_entities(self) -> BlockEntityDict:
        """
        Property that returns the chunk's block entity list. Setting this property replaces the chunk's block entity list

        :return: A list of all the block entities contained in the chunk
        """
        return self._block_entities

    @block_entities.setter
    def block_entities(self, value: BlockEntityDict.InputType):
        """
        :param value: The new block entity list
        :type value: list
        :return:
        """
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
