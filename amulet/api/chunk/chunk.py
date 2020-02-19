from __future__ import annotations

from typing import Tuple, Union, Iterable, List
import time
import numpy
import pickle
import gzip

from amulet.api.chunk import Biomes, Blocks, Status, BlockEntityDict, EntityList
from amulet.api.entity import Entity

PointCoordinates = Tuple[int, int, int]
SliceCoordinates = Tuple[slice, slice, slice]


class Chunk:
    """
    Class to represent a chunk that exists in an Minecraft world
    """

    def __init__(self, cx: int, cz: int):
        self._cx, self._cz = cx, cz
        self._changed = False
        self._changed_time = 0.0

        self._blocks = None
        self._biomes = Biomes(self, numpy.zeros((16, 16), dtype=numpy.uint32))
        self._entities = EntityList(self)
        self._block_entities = BlockEntityDict(self)
        self._status = Status(self)
        self.misc = {}  # all entries that are not important enough to get an attribute

    def __repr__(self):
        return f"Chunk({self.cx}, {self.cz}, {repr(self._blocks)}, {repr(self._entities)}, {repr(self._block_entities)})"

    def pickle(self, file_path: str):
        chunk_data = (
            self._cx,
            self._cz,
            self._changed_time,
            self._changed,
            numpy.array(self.blocks),
            numpy.array(self.biomes),
            self._entities.data,
            tuple(self._block_entities.data.values()),
            self._status.value,
            self.misc
        )
        with gzip.open(file_path, "wb") as fp:
            pickle.dump(chunk_data, fp)

    @classmethod
    def unpickle(cls, file_path: str) -> Chunk:
        with gzip.open(file_path, "rb") as fp:
            chunk_data = pickle.load(fp)
        self = cls(*chunk_data[:2])
        self.changed, self.blocks, self.biomes, self.entities, self.block_entities, self.status, self.misc = chunk_data[3:]
        self._changed_time = chunk_data[2]
        return self

    def __getitem__(self, item):
        if (
            not isinstance(item, tuple)
            or len(item) != 3
            or not (
                isinstance(item[0], int)
                and isinstance(item[1], int)
                and isinstance(item[2], int)
                or (
                    isinstance(item[0], slice)
                    and isinstance(item[1], slice)
                    and isinstance(item[2], slice)
                )
            )
        ):
            raise Exception(f"The item {item} for Selection object does not make sense")

        return SubChunk(item, self)

    @property
    def cx(self):
        """The chunk's x coordinate"""
        return self._cx

    @property
    def cz(self):
        """The chunk's z coordinate"""
        return self._cz

    @property
    def changed(self) -> bool:
        """
        :return: ``True`` if the chunk has been changed, ``False`` otherwise
        """
        return self._changed

    @changed.setter
    def changed(self, value: bool):
        assert isinstance(value, bool), "Changed value must be a bool"
        self._changed = value
        if value:
            self._changed_time = time.time()

    @property
    def changed_time(self) -> float:
        """The last time the chunk was changed
        Used to track if the chunk was changed since the last save snapshot and if the chunk model needs rebuilding"""
        return self._changed_time

    @property
    def blocks(self) -> Blocks:
        if self._blocks is None:
            self._blocks = Blocks(self)
        return self._blocks

    @blocks.setter
    def blocks(self, value: numpy.ndarray):
        if not numpy.array_equal(self._blocks, value):
            assert value.shape == (
                16,
                256,
                16,
            ), "Shape of the Block array must be (16, 256, 16)"
            assert numpy.issubdtype(
                value.dtype, numpy.integer
            ), "dtype must be an unsigned integer"
            self.changed = True
            self._blocks = Blocks(self, value)

    @property
    def biomes(self) -> Biomes:
        return self._biomes

    @biomes.setter
    def biomes(self, value: numpy.ndarray):
        if not numpy.array_equal(self._biomes, value):
            assert value.size in [
                0,
                256,
                1024,
            ], "Size of the Biome array must be 256 or 1024"
            numpy.issubdtype(
                value.dtype, numpy.integer
            ), "dtype must be an unsigned integer"
            self.changed = True
            self._biomes = Biomes(self, value)

    @property
    def entities(self) -> List[Entity]:
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
            self.changed = True
            self._entities = EntityList(self, value)

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
            self.changed = True
            self._block_entities = BlockEntityDict(self, value)

    @property
    def status(self) -> Status:
        return self._status

    @status.setter
    def status(self, value: Union[float, int, str]):
        self._status.value = value


class SubChunk:
    """
    Class to represent a sub-selection of a chunk
    """

    def __init__(
        self,
        sub_selection_slice: Union[PointCoordinates, SliceCoordinates],
        parent: Chunk,
    ):
        self._sub_selection_slice = sub_selection_slice
        self._parent = parent

    @property
    def parent_coordinates(self) -> Tuple[int, int]:
        """
        :return: The chunk x and z coordinates for the parent chunk
        """
        return self._parent.cx, self._parent.cz

    @property
    def blocks(self) -> numpy.ndarray:
        """
        :return: A 3d array of blocks in the sub-selection
        """
        return self._parent.blocks[self._sub_selection_slice]

    @blocks.setter
    def blocks(self, value):
        """
        :param value: A new numpy array of blocks for the sub-selection
        :type value: numpy.ndarray
        :return:
        """
        temp_blocks = self._parent.blocks.copy()
        temp_blocks[self._sub_selection_slice] = value
        self._parent.blocks = temp_blocks
