from __future__ import annotations

import math as math
import types

import numpy as numpy
from numpy import ndarray, uint8, zeros

__all__ = [
    "ChunkCoordinates",
    "block_coords_to_chunk_coords",
    "blocks_slice_to_chunk_slice",
    "chunk_coords_to_block_coords",
    "chunk_coords_to_region_coords",
    "decode_long_array",
    "encode_long_array",
    "from_nibble_array",
    "math",
    "ndarray",
    "numpy",
    "region_coords_to_chunk_coords",
    "to_nibble_array",
    "uint8",
    "zeros",
]

def block_coords_to_chunk_coords(
    *args: int, sub_chunk_size: int = 16
) -> tuple[int, ...]:
    """

    Converts the supplied block coordinates into chunk coordinates

    :param args: The coordinate of the block(s)
    :param sub_chunk_size: The dimension of the chunk (Optional. Default 16)
    :return: The resulting chunk coordinates in (x, z) order

    """

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

def chunk_coords_to_region_coords(cx: int, cz: int) -> ChunkCoordinates:
    """

    Converts the supplied chunk coordinates into region coordinates

    :param cx: The x coordinate of the chunk
    :param cz: The z coordinate of the chunk
    :return: The resulting region coordinates in (x, z) order

    """

def decode_long_array(
    long_array: numpy.ndarray,
    size: int,
    bits_per_entry: int,
    dense: bool = True,
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

def encode_long_array(
    array: numpy.ndarray,
    bits_per_entry: int | None = None,
    dense: bool = True,
    min_bits_per_entry: int = 1,
) -> numpy.ndarray:
    """

    Encode a long array (from BlockStates or Heightmaps)

    :param array: A numpy array of the data to be encoded.
    :param bits_per_entry: The number of bits to use to store each value. If left as None will use the smallest bits per entry.
    :param dense: If true the long arrays will be treated as a bit stream. If false they are distinct values with padding
    :param min_bits_per_entry: The mimimum value that bits_per_entry can be. If it is less than this it will be capped at this value.
    :return: Encoded array as numpy array

    """

def from_nibble_array(arr: ndarray) -> ndarray:
    """

    Unpacks a flat nibble array into a full size numpy array

    :param arr: The nibble array
    :return: The resulting array

    """

def region_coords_to_chunk_coords(rx: int, rz: int) -> ChunkCoordinates:
    """

    Converts the supplied region coordinates into the minimum chunk coordinates of that region

    :param rx: The x coordinate of the region
    :param rz: The y coordinate of the region
    :return: The resulting minimum chunk coordinates of that region in (x, z) order

    """

def to_nibble_array(arr: ndarray) -> ndarray:
    """

    packs a full size numpy array into a nibble array.

    :param arr: Full numpy array
    :return: The nibble array

    """

ChunkCoordinates: types.GenericAlias  # value = tuple[int, int]