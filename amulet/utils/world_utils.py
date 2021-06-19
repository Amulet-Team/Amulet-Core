from __future__ import annotations

import math
import sys
import gzip
from io import StringIO
from typing import Tuple, Optional
import numpy
from numpy import ndarray, zeros, uint8
from amulet.api.data_types import ChunkCoordinates

SECTOR_BYTES = 4096
SECTOR_INTS = SECTOR_BYTES / 4
CHUNK_HEADER_SIZE = 5
VERSION_GZIP = 1
VERSION_DEFLATE = 2


def block_coords_to_chunk_coords(
    *args: int, sub_chunk_size: int = 16
) -> Tuple[int, ...]:
    """
    Converts the supplied block coordinates into chunk coordinates

    :param args: The coordinate of the block(s)
    :param sub_chunk_size: The dimension of the chunk (Optional. Default 16)
    :return: The resulting chunk coordinates in (x, z) order
    """
    return tuple(int(math.floor(coord / sub_chunk_size)) for coord in args)


def chunk_coords_to_block_coords(
    x: int, z: int, chunk_x_size: int = 16, chunk_z_size: int = 16
) -> ChunkCoordinates:
    """
    Converts the supplied chunk coordinates into block coordinates

    :param x: The x coordinate of the chunk
    :param z: The z coordinate of the chunk
    :param chunk_x_size: The dimension of the chunk in the x direction (Optional. Default 16)
    :param chunk_z_size: The dimension of the chunk in the z direction (Optional. Default 16)
    :return: The resulting block coordinates in (x, z) order
    """
    return x * chunk_x_size, z * chunk_z_size


def chunk_coords_to_region_coords(cx: int, cz: int) -> ChunkCoordinates:
    """
    Converts the supplied chunk coordinates into region coordinates

    :param cx: The x coordinate of the chunk
    :param cz: The z coordinate of the chunk
    :return: The resulting region coordinates in (x, z) order
    """
    return cx >> 5, cz >> 5


def region_coords_to_chunk_coords(rx: int, rz: int) -> ChunkCoordinates:
    """
    Converts the supplied region coordinates into the minimum chunk coordinates of that region

    :param rx: The x coordinate of the region
    :param rz: The y coordinate of the region
    :return: The resulting minimum chunk coordinates of that region in (x, z) order
    """
    return rx << 5, rz << 5


def blocks_slice_to_chunk_slice(
    blocks_slice: slice, chunk_shape: int, chunk_coord: int
) -> slice:
    """
    Converts the supplied blocks slice into chunk slice

    :param blocks_slice: The slice of the blocks
    :param chunk_shape: The shape of the chunk in this direction
    :param chunk_coord: The coordinate of the chunk in this direction
    :return: The resulting chunk slice
    """
    return slice(
        min(max(0, blocks_slice.start - chunk_coord * chunk_shape), chunk_shape),
        min(max(0, blocks_slice.stop - chunk_coord * chunk_shape), chunk_shape),
    )


def gunzip(data):
    """
    Decompresses data that is in Gzip format
    """
    return gzip.GzipFile(fileobj=StringIO(data)).read()


def from_nibble_array(arr: ndarray) -> ndarray:
    """
    Unpacks a flat nibble array into a full size numpy array

    :param arr: The nibble array
    :return: The resulting array
    """
    shape = arr.size

    new_arr = zeros((shape * 2), dtype=uint8)

    new_arr[::2] = arr & 0xF
    new_arr[1::2] = arr >> 4

    return new_arr


def to_nibble_array(arr: ndarray) -> ndarray:
    """
    packs a full size numpy array into a nibble array.

    :param arr: Full numpy array
    :return: The nibble array
    """
    arr = arr.ravel()
    return (arr[::2] + (arr[1::2] << 4)).astype("uint8")


def decode_long_array(
    long_array: numpy.ndarray,
    size: int,
    dense=True,
    bits_per_entry: Optional[int] = None,
) -> numpy.ndarray:
    """
    Decode a long array (from BlockStates or Heightmaps)

    :param long_array: Encoded long array
    :param size: The expected size of the returned array
    :param bits_per_entry: The number of bits per entry in the encoded array.
    :return: Decoded array as numpy array
    """
    long_array = long_array.astype(">q")
    if bits_per_entry is None:
        bits_per_entry = (len(long_array) * 64) // size
        if not dense and bits_per_entry >= 11:
            raise Exception(
                f"The bit size of the array is ambiguous. The bits_per_entry input must be given."
            )
    else:
        if dense:
            expected_len = math.ceil(size * bits_per_entry / 64)
        else:
            expected_len = math.ceil(size / (64 // bits_per_entry))
        if len(long_array) != expected_len:
            raise Exception(
                f"{'Dense e' if dense else 'E'}ncoded long array with {bits_per_entry} bits per entry should contain {expected_len} longs but got {len(long_array)}."
            )

    bits = numpy.unpackbits(long_array[::-1].astype(">i8").view("uint8"))
    if not dense:
        entry_per_long = 64 // bits_per_entry
        bits = bits.reshape(-1, 64)[:, -entry_per_long * bits_per_entry :]

    byte_length = 2 ** math.ceil(math.log(math.ceil(bits_per_entry / 8), 2))

    dtype = {1: "B", 2: ">H", 4: ">I", 8: ">Q"}[byte_length]

    return numpy.packbits(
        numpy.pad(
            bits.reshape(-1, bits_per_entry)[-size:, :],
            [(0, 0), (byte_length * 8 - bits_per_entry, 0)],
            "constant",
        )
    ).view(dtype=dtype)[::-1]


def encode_long_array(
    array: numpy.ndarray,
    dense: bool = True,
    bits_per_entry: Optional[int] = None,
    min_bits_per_entry=4,
) -> numpy.ndarray:
    """
    Encode a long array (from BlockStates or Heightmaps)

    :param array: A numpy array of the data to be encoded.
    :param dense: If true the long arrays will be treated as a bit stream. If false they are distinct values with padding
    :param bits_per_entry: The number of bits to use to store each value. If left as None will use the smallest bits per entry.
    :return: Encoded array as numpy array
    """
    array = array.astype(">Q")
    required_bits_per_entry = max(
        int(numpy.amax(array)).bit_length(), min_bits_per_entry
    )
    if bits_per_entry is None:
        bits_per_entry = required_bits_per_entry
    else:
        if required_bits_per_entry > bits_per_entry:
            raise Exception(
                f"The array requires at least {required_bits_per_entry} bits per value which is more than the specified {bits_per_entry} bits"
            )
    bits = numpy.unpackbits(numpy.ascontiguousarray(array[::-1]).view("uint8")).reshape(
        -1, 64
    )[:, -bits_per_entry:]
    if not dense:
        entry_per_long = 64 // bits_per_entry
        if bits.shape[0] % entry_per_long:
            bits = numpy.pad(
                bits,
                [(entry_per_long - (bits.shape[0] % entry_per_long), 0), (0, 0)],
                "constant",
            )
        bits = numpy.pad(
            bits.reshape(-1, bits_per_entry * entry_per_long),
            [(0, 0), (64 - bits_per_entry * entry_per_long, 0)],
            "constant",
        )

    return numpy.packbits(bits).view(dtype=">q")[::-1]


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
    max_number = numpy.amax(arr)
    if not uint:
        max_number = max_number * 2
    if max_number == 0:
        max_number = 1
    return next(dtype for dtype in possible_dtypes if dtype > math.log(max_number, 2))


def entity_position_to_chunk_coordinates(
    entity_coordinates: Tuple[float, float, float]
):
    return (
        int(math.floor(entity_coordinates[0])) >> 4,
        int(math.floor(entity_coordinates[2])) >> 4,
    )


def fast_unique(array: numpy.ndarray) -> Tuple[numpy.ndarray, numpy.ndarray]:
    uni = numpy.unique(array)
    lut = numpy.zeros(numpy.amax(uni) + 1, dtype=numpy.uint32)
    lut[uni] = numpy.arange(uni.size)
    inv = lut[array]
    return uni, inv
