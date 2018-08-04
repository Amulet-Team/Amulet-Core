import gzip
from io import StringIO
from typing import Union, Tuple
from numpy import ndarray, zeros, uint8

Coordinates = Tuple[int, int]

SECTOR_BYTES = 4096
SECTOR_INTS = SECTOR_BYTES / 4
CHUNK_HEADER_SIZE = 5
VERSION_GZIP = 1
VERSION_DEFLATE = 2


def block_coords_to_chunk_coords(x: int, z: int) -> Coordinates:
    """
    Converts the supplied block coordinates into chunk coordinates

    :param x: The x coordinate of the block
    :param z: The z coordinate of the block
    :return: The resulting chunk coordinates in (x, z) order
    """
    return x >> 4, z >> 4


def chunk_coords_to_region_coords(cx: int, cz: int) -> Coordinates:
    """
    Converts the supplied chunk coordinates into region coordinates

    :param cx: The x coordinate of the chunk
    :param cz: The z coordinate of the chunk
    :return: The resulting region coordinates in (x, z) order
    """
    return cx >> 5, cz >> 5


def region_coords_to_chunk_coords(rx: int, rz: int) -> Coordinates:
    """
    Converts the supplied region coordinates into the minimum chunk coordinates of that region

    :param rx: The x coordinate of the region
    :param rz: The y coordinate of the region
    :return: The resulting minimum chunk coordinates of that region in (x, z) order
    """
    return rx << 5, rz << 5


def gunzip(data):
    """
    Decompresses data that is in Gzip format
    """
    return gzip.GzipFile(fileobj=StringIO(data)).read()


def fromNibbleArray(arr: ndarray) -> ndarray:
    """
    Unpacks a nibble array into a full size numpy array

    :param arr: The nibble array
    :return: The resulting array
    """
    shape = arr.shape

    new_arr = zeros((shape[0], shape[1], shape[2] * 2), dtype=uint8)

    new_arr[:, :, ::2] = arr
    new_arr[:, :, ::2] &= 0xf
    new_arr[:, :, 1::2] = arr
    new_arr[:, :, 1::2] >>= 4

    return new_arr


import sys


def get_size(obj, seen=None):
    """Recursively finds size of objects"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0

    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, "__dict__"):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, "__iter__") and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])
    return size


class InternalBlockMap:

    def __init__(self):
        # self._mapping = {"minecraft:air": 0}
        # self._reverse_mapping = {0: "minecraft:air"}
        self._mapping = ["minecraft:air"]
        self._next_id = 1
        self._next_unknown = 0

        # self.__getitem__ = self._mapping.__getitem__
        # self.__setitem__ = self._mapping.__setitem__
        # self.__delitem__ = self._mapping.__delitem__

        self.__contains__ = self._mapping.__contains__

    def add_entry(self, entry: str) -> int:
        if entry in self._mapping:
            return self.get_entry(entry)

        if not entry:
            self._mapping.insert(
                self._next_id, "minecraft:unknown_{}".format(self._next_unknown)
            )
            self._next_unknown += 1
        else:
            self._mapping.insert(self._next_id, entry)
        self._next_id += 1
        return self._next_id - 1

    def __getitem__(self, item):
        return self._mapping[item]

    def get_entry(self, entry: Union[str, int]) -> Union[str, int]:
        if isinstance(entry, str):
            return self._mapping.index(entry)

        elif isinstance(entry, int):
            return self._mapping[entry]

        else:
            raise KeyError()

    def __str__(self):
        return "next_id: {}, {}".format(self._next_id, self._mapping)
