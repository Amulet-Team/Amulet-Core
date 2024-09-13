from __future__ import annotations

import numpy
import typing_extensions

__all__ = ["decode_long_array", "encode_long_array"]

def decode_long_array(
    long_array: typing_extensions.Buffer,
    size: int,
    bits_per_entry: int,
    dense: bool = True,
) -> numpy.ndarray:
    """
    Decode a long array (from BlockStates or Heightmaps)

    :param long_array: Encoded long array
    :param size: The expected size of the returned array
    :param bits_per_entry: The number of bits per entry in the encoded array.
    :param dense: If true the long arrays will be treated as a bit stream. If false they are distinct values with padding
    :return: Decoded array as numpy array
    """

def encode_long_array(
    array: typing_extensions.Buffer,
    bits_per_entry: None | int = None,
    dense: bool = True,
    min_bits_per_entry: int = 1,
) -> numpy.ndarray[numpy.uint64]:
    """
    Encode a long array (from BlockStates or Heightmaps)

    :param array: A numpy array of the data to be encoded.
    :param bits_per_entry: The number of bits to use to store each value. If left as None will use the smallest bits per entry.
    :param dense: If true the long arrays will be treated as a bit stream. If false they are distinct values with padding
    :param min_bits_per_entry: The mimimum value that bits_per_entry can be. If it is less than this it will be capped at this value.
    :return: Encoded array as numpy array
    """
