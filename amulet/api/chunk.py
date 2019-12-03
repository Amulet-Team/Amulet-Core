from __future__ import annotations

import copy
from os.path import join
import pickle
from typing import Tuple, Union, Iterable, List

import numpy

from .chunk_data import Biomes, Blocks, Status, BlockEntityList, EntityList
from amulet.api.entity import Entity
from amulet.api.block_entity import BlockEntity

PointCoordinates = Tuple[int, int, int]
SliceCoordinates = Tuple[slice, slice, slice]


class Chunk:
    """
    Class to represent a chunk that exists in an Minecraft world
    """

    def __init__(self, cx: int, cz: int):
        self.cx, self.cz = cx, cz
        self._changed = False
        self._marked_for_deletion = False

        self._blocks = None
        self._biomes = Biomes(self, numpy.zeros((16, 16), dtype=numpy.uint32))
        self._entities = EntityList(self)
        self._block_entities = BlockEntityList(self)
        self._status = Status(self)
        self.misc = {}  # all entries that are not important enough to get an attribute

    def __repr__(self):
        return f"Chunk({self.cx}, {self.cz}, {repr(self._blocks)}, {repr(self._entities)}, {repr(self._block_entities)})"

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
    def changed(self) -> bool:
        """
        :return: ``True`` if the chunk has been changed, ``False`` otherwise
        """
        return self._changed

    @changed.setter
    def changed(self, value: bool):
        self._changed = value

    @property
    def marked_for_deletion(self) -> bool:
        """
        :return: ``True`` if the chunk has been marked for deletion, ``False`` otherwise
        """
        return self._marked_for_deletion

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
    def entities(self) -> EntityList[Entity]:
        """
        Property that returns the chunk's entity list. Setting this property replaces the chunk's entity list

        :param value: The new entity list
        :type value: list
        :return: A list of all the entities contained in the chunk
        """
        return self._entities

    @entities.setter
    def entities(self, value: Iterable[Entity]):
        if self._entities != value:
            self.changed = True
            self._entities = EntityList(self, value)

    @property
    def block_entities(self) -> List[BlockEntity]:
        """
        Property that returns the chunk's block entity list. Setting this property replaces the chunk's block entity list

        :param value: The new block entity list
        :type value: list
        :return: A list of all the block entities contained in the chunk
        """
        return self._block_entities

    @block_entities.setter
    def block_entities(self, value: Iterable[BlockEntity]):
        if self._block_entities != value:
            self.changed = True
            self._block_entities = BlockEntityList(self, value)

    @property
    def status(self) -> Status:
        return self._status

    @status.setter
    def status(self, value: Union[float, int, str]):
        self._status.set_value(value)

    def serialize_chunk(self, change_path) -> str:
        """
        Serialized the chunk to a file on the disk in the supplied directory path. The filename follows the convention: ``<cx>.<cz>.chunk``

        :param change_path: The directory path to save the chunk at
        :return: The full path to the serialized chunk file
        """
        save_path = join(change_path, f"{self.cx}.{self.cz}.chunk")

        fp = open(save_path, "wb")
        pickle.dump(self, fp)
        fp.close()

        return save_path

    @classmethod
    def unserialize_chunk(cls, change_path) -> Chunk:
        """
        Unserializes chunk from the given file path.

        :param change_path: The file to unserialize
        :return: The recreated :class:`api.chunk.Chunk` object
        """
        fp = open(change_path, "rb")
        chunk = pickle.load(fp)
        fp.close()

        return chunk

    def delete(self):
        """
        Marks the given chunk for deletion
        """
        self._marked_for_deletion = True
        self.changed = True


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
        :param value: A new numpy array of blocks for the sub-selection
        :type value: numpy.ndarray
        :return: A 3d array of blocks in the sub-selection
        """
        return self._parent.blocks[self._sub_selection_slice]

    @blocks.setter
    def blocks(self, value):
        temp_blocks = self._parent.blocks.copy()
        temp_blocks[self._sub_selection_slice] = value
        self._parent.blocks = temp_blocks
