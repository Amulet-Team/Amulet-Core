from __future__ import annotations

import math
import sys
import gzip
from io import StringIO
from typing import Tuple, Optional
import numpy
from numpy import ndarray, zeros, uint8
from amulet.api.data_types import ChunkCoordinates


# depreciated and will be removed
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


"""
Minecraft Java edition stores the block and height arrays in a compacted long array format.
The format stores one or more entries per long, using the fewest number of bits required to store the data.
There are two storage methods, the compact version was used prior to 1.16 and the less compact version in 1.16 and above.
Apparently the less compact version is quicker to pack and unpack.
The compact version effectively stores the values as a bit array spanning one or more values in the long array.
There may be some padding if the bit array does not fill all the long values. (The letter "P" signifies an unused padding bit)
PPAAAAAAAAABBBBBBBBBCCCCCCCCCDDDDDDDDDEEEEEEEEEFFFFFFFFFGGGGGGGG GHHHHHHHHHIIIIIIIIIJJJJJJJJJKKKKKKKKKLLLLLLLLLMMMMMMMMMOOOOOOOOO
The less compact version does not allow entries to straddle long values. Instead, if required, there is padding within each long.
PAAAAAAAAABBBBBBBBBCCCCCCCCCDDDDDDDDDEEEEEEEEEFFFFFFFFFGGGGGGGGG PHHHHHHHHHIIIIIIIIIJJJJJJJJJKKKKKKKKKLLLLLLLLLMMMMMMMMMOOOOOOOOO

The functions below can be used to pack and unpack both formats.
"""


def decode_long_array(
    long_array: numpy.ndarray,
    size: int,
    bits_per_entry: int,
    dense=True,
    signed: bool = False,
) -> numpy.ndarray:
    """
    Decode a long array (from BlockStates or Heightmaps)

    :param long_array: Encoded long array
    :param size: The expected size of the returned array
    :param bits_per_entry: The number of bits per entry in the encoded array.
    :param dense: If true the long arrays will be treated as a bit stream. If false they are distinct values with padding
    :param signed: Should the returned array be signed.
    :return: Decoded array as numpy array
    """
    # validate the inputs and throw an error if there is a problem
    if not isinstance(bits_per_entry, int):
        raise ValueError(f"The bits_per_entry input must be an int.")

    assert (
        1 <= bits_per_entry <= 64
    ), f"bits_per_entry must be between 1 and 64 inclusive. Got {bits_per_entry}"

    # force the array to be a signed long array
    long_array = long_array.astype(">q")

    if dense:
        expected_len = math.ceil(size * bits_per_entry / 64)
    else:
        expected_len = math.ceil(size / (64 // bits_per_entry))
    if len(long_array) != expected_len:
        raise Exception(
            f"{'Dense e' if dense else 'E'}ncoded long array with {bits_per_entry} bits per entry should contain {expected_len} longs but got {len(long_array)}."
        )

    # unpack the long array into a bit array
    bits = numpy.unpackbits(long_array[::-1].astype(">i8").view("uint8"))
    if dense:
        if bits.size % bits_per_entry:
            # if the array is densely packed and there is extra padding, remove it
            bits = bits[bits.size % bits_per_entry :]
    else:
        # if not densely packed remove the padding per long
        entry_per_long = 64 // bits_per_entry
        bits = bits.reshape(-1, 64)[:, -entry_per_long * bits_per_entry :]

    byte_length = 2 ** math.ceil(math.log(math.ceil(bits_per_entry / 8), 2))
    dtype = {1: "B", 2: ">H", 4: ">I", 8: ">Q"}[byte_length]

    # pad the bits to fill one of the above data types
    arr = numpy.packbits(
        numpy.pad(
            bits.reshape(-1, bits_per_entry)[-size:, :],
            [(0, 0), (byte_length * 8 - bits_per_entry, 0)],
            "constant",
        )
    ).view(dtype=dtype)[::-1]
    if signed:
        # convert to a signed array if requested
        sarray = arr.astype({1: "b", 2: ">h", 4: ">i", 8: ">q"}[byte_length])
        if bits_per_entry < 64:
            mask = arr >= 2 ** (bits_per_entry - 1)
            sarray[mask] = numpy.subtract(
                arr[mask], 2**bits_per_entry, dtype=numpy.int64
            )
        arr = sarray
    return arr


def encode_long_array(
    array: numpy.ndarray,
    bits_per_entry: Optional[int] = None,
    dense: bool = True,
    min_bits_per_entry=1,
) -> numpy.ndarray:
    """
    Encode a long array (from BlockStates or Heightmaps)

    :param array: A numpy array of the data to be encoded.
    :param bits_per_entry: The number of bits to use to store each value. If left as None will use the smallest bits per entry.
    :param dense: If true the long arrays will be treated as a bit stream. If false they are distinct values with padding
    :param min_bits_per_entry: The mimimum value that bits_per_entry can be. If it is less than this it will be capped at this value.
    :return: Encoded array as numpy array
    """
    assert (
        1 <= min_bits_per_entry <= 64
    ), f"min_bits_per_entry must be between 1 and 64 inclusive. Got {bits_per_entry}"
    # cast to a signed longlong array
    array = array.astype(">q")
    # work out how many bits are required to store the
    required_bits_per_entry = max(
        max(
            int(numpy.amin(array)).bit_length(),
            int(numpy.amax(array)).bit_length(),
        ),
        min_bits_per_entry,
    )
    if bits_per_entry is None:
        # if a bit depth has not been requested use the minimum required
        bits_per_entry = required_bits_per_entry
    elif isinstance(bits_per_entry, int):
        assert (
            1 <= bits_per_entry <= 64
        ), f"bits_per_entry must be between 1 and 64 inclusive. Got {bits_per_entry}"
        # if a bit depth has been set and it is smaller than what is required throw an error
        if required_bits_per_entry > bits_per_entry:
            raise Exception(
                f"The array requires at least {required_bits_per_entry} bits per value which is more than the specified {bits_per_entry} bits"
            )
    else:
        raise ValueError(
            "bits_per_entry must be an int between 1 and 64 inclusive or None."
        )
    # make the negative values positive to make bit storage easier
    uarray = array.astype(">Q")
    if bits_per_entry < 64:
        mask = array < 0
        uarray[mask] = numpy.add(
            array[mask], 2**bits_per_entry, dtype=numpy.uint64, casting="unsafe"
        )
    array = uarray

    # unpack the individual values into a bit array
    bits: numpy.ndarray = numpy.unpackbits(
        numpy.ascontiguousarray(array[::-1]).view("uint8")
    ).reshape(-1, 64)[:, -bits_per_entry:]
    if dense:
        if bits.size % 64:
            # if the bit array does not fill a whole long
            # add padding to the last long if required
            bits = numpy.pad(
                bits.ravel(),
                [(64 - (bits.size % 64), 0)],
                "constant",
            )
    else:
        # if the array is not dense add padding
        entry_per_long = 64 // bits_per_entry
        if bits.shape[0] % entry_per_long:
            # add padding to the last long if required
            bits = numpy.pad(
                bits,
                [(entry_per_long - (bits.shape[0] % entry_per_long), 0), (0, 0)],
                "constant",
            )
        # add padding for each long
        bits = numpy.pad(
            bits.reshape(-1, bits_per_entry * entry_per_long),
            [(0, 0), (64 - bits_per_entry * entry_per_long, 0)],
            "constant",
        )

    # pack the bits into a long array
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
    possible_dtypes = (2**x for x in range(3, 8))
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
