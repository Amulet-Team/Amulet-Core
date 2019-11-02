from __future__ import annotations

from math import log
import sys
import gzip
from io import StringIO
from typing import Tuple
import numpy
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


def chunk_coords_to_block_coords(x: int, z: int) -> Coordinates:
    """
    Converts the supplied chunk coordinates into block coordinates

    :param x: The x coordinate of the chunk
    :param z: The z coordinate of the chunk
    :return: The resulting block coordinates in (x, z) order
    """
    return x << 4, z << 4


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


def blocks_slice_to_chunk_slice(blocks_slice: slice) -> slice:
    """
    Converts the supplied blocks slice into chunk slice
    :param blocks_slice: The slice of the blocks
    :return: The resulting chunk slice
    """
    return slice(blocks_slice.start % 16, blocks_slice.stop % 16)


def gunzip(data):
    """
    Decompresses data that is in Gzip format
    """
    return gzip.GzipFile(fileobj=StringIO(data)).read()


def from_nibble_array(arr: ndarray) -> ndarray:
    """
    Unpacks a nibble array into a full size numpy array

    :param arr: The nibble array
    :return: The resulting array
    """
    shape = arr.shape

    new_arr = zeros((shape[0], shape[1], shape[2] * 2), dtype=uint8)

    new_arr[:, :, ::2] = arr
    new_arr[:, :, ::2] &= 0xF
    new_arr[:, :, 1::2] = arr
    new_arr[:, :, 1::2] >>= 4

    return new_arr


def decode_long_array(long_array: numpy.ndarray, size: int) -> numpy.ndarray:
    """
    Decode an long array (from BlockStates or Heightmaps)
    :param long_array: Encoded long array
    :size uint: The expected size of the returned array
    :return: Decoded array as numpy array
    """
    long_array = long_array.astype(">q")
    bits_per_entry = (len(long_array) * 64) // size

    return numpy.packbits(
        numpy.pad(
            numpy.unpackbits(long_array[::-1].astype(">i8").view("uint8")).reshape(
                -1, bits_per_entry
            ),
            [(0, 0), (64 - bits_per_entry, 0)],
            "constant",
        )
    ).view(dtype=">q")[::-1]


def encode_long_array(array: numpy.ndarray) -> numpy.ndarray:
    """
    Encode an long array (from BlockStates or Heightmaps)
    :param array: A numpy array of the data to be encoded.
    :return: Encoded array as numpy array
    """
    array = array.astype(">q")
    bits_per_entry = max(int(array.max()).bit_length(), 2)
    return numpy.packbits(
        numpy.unpackbits(numpy.ascontiguousarray(array[::-1]).view("uint8")).reshape(-1, 64)[:, -bits_per_entry:]
    ).view(dtype=">q")[::-1]


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


def get_smallest_dtype(arr: ndarray, uint: bool = True) -> int:
    """
    Returns the smallest dtype (number) that the array can afford
    :param arr: The array to check on
    :param uint: Should the array fit in uint or not (default: True)
    :return: The number of bits all the elements can be represented with
    """
    possible_dtypes = (2 ** x for x in range(3, 8))
    max_number = arr.max()
    if not uint:
        max_number = max_number * 2
    if max_number == 0:
        max_number = 1
    return next(dtype for dtype in possible_dtypes if dtype > log(max_number, 2))


def entity_position_to_chunk_coordinates(
    entity_coordinates: Tuple[float, float, float]
):
    return int(entity_coordinates[0]) >> 4, int(entity_coordinates[2]) >> 4


def get_entity_coordinates(ent) -> Tuple[float, float, float]:
    return tuple(ent["Pos"])
