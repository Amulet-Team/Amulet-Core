from __future__ import annotations

import copy
from os.path import join
import pickle
from typing import Tuple, Union

import numpy

PointCoordinates = Tuple[int, int, int]
SliceCoordinates = Tuple[slice, slice, slice]


class Chunk:
    """
    Class to represent a chunk that exists in an Minecraft world
    """

    def __init__(self, cx: int, cz: int, blocks=None, entities=None, tileentities=None):
        self.cx, self.cz = cx, cz
        self._blocks: numpy.ndarray = blocks
        self._entities = entities
        self._tileentities = tileentities

        self._changed = False
        self._marked_for_deletion = False

    def __repr__(self):
        return f"Chunk({self.cx}, {self.cx}, {repr(self._blocks)}, {repr(self._entities)}, {repr(self._tileentities)})"

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

    @property
    def marked_for_deletion(self) -> bool:
        """
        :return: ``True`` if the chunk has been marked for deletion, ``False`` otherwise
        """
        return self._marked_for_deletion

    @property
    def blocks(self) -> numpy.ndarray:
        """
        Property that returns a read-only copy of the chunk's block array. Setting this property replaces the entire chunk's block array

        :param value: The new block array
        :type value: numpy.ndarray
        :return: A 3d numpy array of the internal Block IDs for the chunk
        """
        self._blocks.setflags(write=False)
        return self._blocks

    @blocks.setter
    def blocks(self, value: numpy.ndarray):
        if not (self._blocks == value).all():
            self._changed = True
        self._blocks = value

    @property
    def entities(self) -> list:
        """
        Property that returns a copy of the chunk's entity list. Setting this property replaces the chunk's entity list

        :param value: The new entity list
        :type value: list
        :return: A list of all the entities contained in the chunk
        """
        return copy.deepcopy(self._entities)

    @entities.setter
    def entities(self, value):
        if self._entities != value:
            self._changed = True
            self._entities = value

    @property
    def tileentities(self) -> list:
        """
        Property that returns a copy of the chunk's tile entity list. Setting this property replaces the chunk's tile entity list

        :param value: The new tile entity list
        :type value: list
        :return: A list of all the tile entities contained in the chunk
        """
        return copy.deepcopy(self._tileentities)

    @tileentities.setter
    def tileentities(self, value):
        if self._tileentities != value:
            self._changed = True
            self._tileentities = value

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
        self._changed = True


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
