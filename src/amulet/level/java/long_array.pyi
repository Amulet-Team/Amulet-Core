from __future__ import annotations

import numpy
import typing_extensions

__all__ = ["decode_long_array"]

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
