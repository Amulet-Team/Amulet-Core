from __future__ import annotations

import copy
from os.path import join
import pickle
from typing import Tuple, Union, Dict, Any

import numpy

import amulet_nbt as nbt

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
        self._entities = None
        self._tileentities = None
        self.misc = {}  # all entries that are not important enough to get an attribute
        self.extra = {}  # temp store for Java NBTFile. Remove this when unpacked to misc

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
            self.changed = True
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
            self.changed = True
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


class ChunkArray(numpy.ndarray):
    def __new__(cls, parent_chunk: Chunk, input_array):
        obj = numpy.asarray(input_array).view(cls)
        obj._parent_chunk = parent_chunk
        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self._parent_chunk = getattr(obj, "_parent_chunk", None)

    def _dirty(self):
        self._parent_chunk.changed = True

    def byteswap(self, inplace=False):
        if inplace:
            self._dirty()
        numpy.ndarray.byteswap(self, inplace)

    def fill(self, value):
        self._dirty()
        numpy.ndarray.fill(self, value)

    def itemset(self, *args):
        self._dirty()
        numpy.ndarray.itemset(*args)

    def partition(self, kth, axis=-1, kind="introselect", order=None):
        self._dirty()
        numpy.ndarray.partition(self, kth, axis, kind, order)

    def put(self, indices, values, mode="raise"):
        self._dirty()
        numpy.ndarray.put(self, indices, values, mode)

    def resize(self, *new_shape, refcheck=True):
        self._dirty()
        numpy.ndarray.resize(self, *new_shape, refcheck=refcheck)

    def sort(self, axis=-1, kind="quicksort", order=None):
        self._dirty()
        numpy.ndarray.sort(self, axis, kind, order)

    def squeeze(self, axis=None):
        self._dirty()
        numpy.ndarray.squeeze(self, axis)

    def __iadd__(self, *args, **kwargs):
        self._dirty()
        numpy.ndarray.__iadd__(self, *args, **kwargs)

    def __iand__(self, *args, **kwargs):
        self._dirty()
        numpy.ndarray.__iand__(self, *args, **kwargs)

    def __ifloordiv__(self, *args, **kwargs):
        self._dirty()
        numpy.ndarray.__ifloordiv__(self, *args, **kwargs)

    def __ilshift__(self, *args, **kwargs):
        self._dirty()
        numpy.ndarray.__ilshift__(self, *args, **kwargs)

    def __imatmul__(self, *args, **kwargs):
        self._dirty()
        numpy.ndarray.__imatmul__(self, *args, **kwargs)

    def __imod__(self, *args, **kwargs):
        self._dirty()
        numpy.ndarray.__imod__(self, *args, **kwargs)

    def __imul__(self, *args, **kwargs):
        self._dirty()
        numpy.ndarray.__imul__(self, *args, **kwargs)

    def __ior__(self, *args, **kwargs):
        self._dirty()
        numpy.ndarray.__ior__(self, *args, **kwargs)

    def __ipow__(self, *args, **kwargs):
        self._dirty()
        numpy.ndarray.__ipow__(self, *args, **kwargs)

    def __irshift__(self, *args, **kwargs):
        self._dirty()
        numpy.ndarray.__irshift__(self, *args, **kwargs)

    def __isub__(self, *args, **kwargs):
        self._dirty()
        numpy.ndarray.__isub__(self, *args, **kwargs)

    def __itruediv__(self, *args, **kwargs):
        self._dirty()
        numpy.ndarray.__itruediv__(self, *args, **kwargs)

    def __ixor__(self, *args, **kwargs):
        self._dirty()
        numpy.ndarray.__ixor__(self, *args, **kwargs)

    def __setitem__(self, *args, **kwargs):
        self._dirty()
        numpy.ndarray.__setitem__(self, *args, **kwargs)


class Blocks(ChunkArray):
    pass


class Biomes(ChunkArray):
    def __new__(cls, parent_chunk: Chunk, input_array):
        obj = numpy.asarray(input_array, dtype=numpy.uint32).view(cls)
        obj._parent_chunk = parent_chunk
        if obj.size == 256:
            obj.resize(16, 16)
        elif obj.size == 1024:
            obj.resize(8, 8, 16)  # TODO: honestly don't know what the format of this is
        return obj

    def convert_to_format(self, length):
        if length in [256, 1024]:
            # TODO: proper conversion
            if length > self.size:
                self._parent_chunk.biomes = numpy.concatenate(
                    (self.ravel(), numpy.zeros(length - self.size, dtype=self.dtype))
                )
            elif length < self.size:
                self._parent_chunk.biomes = self.ravel()[:length]
            return self._parent_chunk.biomes
        else:
            raise Exception(f"Format length {length} is invalid")
