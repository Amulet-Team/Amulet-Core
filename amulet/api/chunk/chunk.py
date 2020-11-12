from __future__ import annotations

from typing import Tuple, Union, Iterable, Dict
import time
import numpy
import pickle
import gzip

from amulet.api.block import Block
from amulet.api.registry import BlockManager
from amulet.api.registry.biome_manager import BiomeManager
from amulet.api.chunk import Biomes, Blocks, Status, BlockEntityDict, EntityList
from amulet.api.entity import Entity
from amulet.api.data_types import ChunkCoordinates
from amulet.api.history.changeable import Changeable

PointCoordinates = Tuple[int, int, int]
SliceCoordinates = Tuple[slice, slice, slice]


class Chunk(Changeable):
    """
    Class to represent a chunk that exists in an Minecraft world
    """

    def __init__(self, cx: int, cz: int):
        super().__init__()
        self._cx, self._cz = cx, cz
        self._changed_time = 0.0

        self._blocks = None
        self.__block_palette = BlockManager()
        self.__biome_palette = BiomeManager()
        self._biomes = None
        self._entities = EntityList()
        self._block_entities = BlockEntityDict()
        self._status = Status(self)
        self.misc = {}  # all entries that are not important enough to get an attribute

    def __repr__(self):
        return f"Chunk({self.cx}, {self.cz}, {repr(self._blocks)}, {repr(self._entities)}, {repr(self._block_entities)})"

    def pickle(self, file_path: str):
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
        )
        with gzip.open(file_path, "wb") as fp:
            pickle.dump(chunk_data, fp)

    @classmethod
    def unpickle(
        cls, file_path: str, block_palette: BlockManager, biome_palette: BiomeManager
    ) -> Chunk:
        with gzip.open(file_path, "rb") as fp:
            chunk_data = pickle.load(fp)
        self = cls(*chunk_data[:2])
        (
            self.blocks,
            biomes,
            self.entities,
            self.block_entities,
            self.status,
            self.misc,
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
        """The chunk's coordinates"""
        return self._cx, self._cz

    @property
    def changed(self) -> bool:
        """
        :return: ``True`` if the chunk has been changed since the last undo point, ``False`` otherwise
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
        """The last time the chunk was changed
        Used to track if the chunk was changed since the last save snapshot and if the chunk model needs rebuilding"""
        return self._changed_time

    @property
    def blocks(self) -> Blocks:
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
        :param dx: The x coordinate within the chunk. 0 is the bottom edge, 15 is the top edge
        :param y: The y coordinate within the chunk. This can be any integer.
        :param dz: The z coordinate within the chunk. 0 is the bottom edge, 15 is the top edge
        :return: The universal Block object representation of the block at that location
        """
        return self.block_palette[self.blocks[dx, y, dz]]

    def set_block(self, dx: int, y: int, dz: int, block: Block):
        """
        Get the universal Block object at the given location within the chunk.
        :param dx: The x coordinate within the chunk. 0 is the bottom edge, 15 is the top edge
        :param y: The y coordinate within the chunk. This can be any integer.
        :param dz: The z coordinate within the chunk. 0 is the bottom edge, 15 is the top edge
        :param block: The universal Block object to set at the given location
        :return:
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
        """The block block_palette for the chunk.
        Usually will refer to a global block block_palette."""
        return self._block_palette

    @block_palette.setter
    def block_palette(self, new_block_palette: BlockManager):
        """Change the block block_palette for the chunk.
        This will copy over all block states from the old block_palette and remap the block indexes to use the new block_palette."""
        assert isinstance(new_block_palette, BlockManager)
        if new_block_palette is not self._block_palette:
            # if current block block_palette and the new block block_palette are not the same object
            if self._block_palette:
                # if there are blocks in the current block block_palette remap the data
                block_lut = numpy.array(
                    [
                        new_block_palette.get_add_block(block)
                        for block in self._block_palette.blocks()
                    ],
                    dtype=numpy.uint,
                )
                for cy in self.blocks.sub_chunks:
                    self.blocks.add_sub_chunk(
                        cy, block_lut[self.blocks.get_sub_chunk(cy)]
                    )

            self.__block_palette = new_block_palette

    @property
    def biomes(self) -> Biomes:
        if self._biomes is None:
            self._biomes = Biomes()
        return self._biomes

    @biomes.setter
    def biomes(self, value: Union[Biomes, Dict[int, numpy.ndarray]]):
        self._biomes = Biomes(value)

    @property
    def _biome_palette(self) -> BiomeManager:
        """The biome block_palette for the chunk.
        Usually will refer to a global biome block_palette."""
        return self.__biome_palette

    @_biome_palette.setter
    def _biome_palette(self, new_biome_palette: BiomeManager):
        """Change the biome block_palette for the chunk.
        This will change the biome block_palette but leave the biome array unchanged.
        Only use this if you know what you are doing.
        Designed for internal use. You probably want to use Chunk.biome_palette"""
        assert isinstance(new_biome_palette, BiomeManager)
        self.__biome_palette = new_biome_palette

    @property
    def biome_palette(self) -> BiomeManager:
        """The biome block_palette for the chunk.
        Usually will refer to a global biome block_palette."""
        return self._biome_palette

    @biome_palette.setter
    def biome_palette(self, new_biome_palette: BiomeManager):
        """Change the biome block_palette for the chunk.
        This will copy over all biome states from the old block_palette and remap the biome indexes to use the new block_palette."""
        assert isinstance(new_biome_palette, BiomeManager)
        if new_biome_palette is not self._biome_palette:
            # if current biome block_palette and the new biome block_palette are not the same object
            if self._biome_palette:
                # if there are biomes in the current biome block_palette remap the data
                biome_lut = numpy.array(
                    [
                        new_biome_palette.get_add_biome(biome)
                        for biome in self._biome_palette.biomes()
                    ],
                    dtype=numpy.uint,
                )
                if self.biomes.dimension == 2:
                    self.biomes = biome_lut[self.biomes]
                elif self.biomes.dimension == 3:
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
        return self._status

    @status.setter
    def status(self, value: Union[float, int, str]):
        self._status.value = value
