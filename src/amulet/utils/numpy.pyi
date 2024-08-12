from __future__ import annotations
import numpy
import typing_extensions

__all__ = ["unique_inverse"]

def unique_inverse(
    arg0: typing_extensions.Buffer,
) -> tuple[numpy.ndarray[numpy.uint32], numpy.ndarray[numpy.uint32]]: ...
