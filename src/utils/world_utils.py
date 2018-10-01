from __future__ import annotations

import numpy
import sys
import gzip
from io import StringIO
from typing import Tuple
from numpy import ndarray, zeros, uint8
from math import log, ceil

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
    new_arr[:, :, ::2] &= 0xf
    new_arr[:, :, 1::2] = arr
    new_arr[:, :, 1::2] >>= 4

    return new_arr


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


def decode_long_array(long_array: array_like, size: int) -> ndarray:
    """
    Decode an long array (from BlockStates or Heightmaps)
    :param long_array: Encoded long array
    :size uint: The expected size of the returned array
    :return: Decoded array as numpy array
    """
    long_array = numpy.array(long_array, dtype=">q")
    bits_per_block = (len(long_array) * 64) // size
    binary_blocks = numpy.unpackbits(
        long_array[::-1].astype(">i8").view("uint8")
    ).reshape(-1, bits_per_block)
    return binary_blocks.dot(2 ** numpy.arange(binary_blocks.shape[1] - 1, -1, -1))[
        ::-1  # Undo the bit-shifting that Minecraft does with the palette indices
    ][:size]


def encode_long_array(data_array: array_like, palette_size: int) -> ndarray:
    """
    Encode an array of data to a long array (from BlockStates or Heightmaps).
    :param long_array: Data to encode
    :palette_size uint: Must be at least 4
    :return: Encoded array as numpy array
    """
    data_array = numpy.array(data_array, dtype=">i2")
    bits_per_block = max(4, int(ceil(log(palette_size, 2))))
    binary_blocks = (
        numpy.unpackbits(data_array.astype(">i2").view("uint8"))
        .reshape(-1, 16)[:, (16 - bits_per_block) :][::-1]
        .reshape(-1)
    )
    binary_blocks = numpy.pad(
        binary_blocks, ((64 - (len(data_array) * bits_per_block)) % 64, 0), "constant"
    ).reshape(-1, 64)
    return binary_blocks.dot(
        2 ** numpy.arange(binary_blocks.shape[1] - 1, -1, -1, dtype=">q")
    )[::-1]