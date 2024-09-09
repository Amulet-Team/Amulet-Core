from __future__ import annotations

import numpy
import numpy.typing
import typing_extensions

__all__ = ["unique_inverse"]

def unique_inverse(
    array: typing_extensions.Buffer,
) -> tuple[numpy.typing.NDArray[numpy.uint32], numpy.typing.NDArray[numpy.uint32]]: ...
