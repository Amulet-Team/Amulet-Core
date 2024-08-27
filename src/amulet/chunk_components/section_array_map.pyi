from __future__ import annotations
import amulet.collections
import numpy
import typing
import typing_extensions

__all__ = ["IndexArray3D", "SectionArrayMap"]

class IndexArray3D:
    """
    A 3D index array.
    """

    def __buffer__(self, flags):
        """
        Return a buffer object that exposes the underlying memory of the object.
        """

    @typing.overload
    def __init__(self, shape: tuple[int, int, int]) -> None: ...
    @typing.overload
    def __init__(self, shape: tuple[int, int, int], value: int) -> None: ...
    @typing.overload
    def __init__(self, other: IndexArray3D) -> None: ...
    @typing.overload
    def __init__(self, arg0: typing_extensions.Buffer) -> None: ...
    def __release_buffer__(self, buffer):
        """
        Release the buffer object that exposes the underlying memory of the object.
        """

    @property
    def shape(self) -> tuple[int, int, int]: ...
    @property
    def size(self) -> int: ...

class SectionArrayMap:
    """
    A container of sub-chunk arrays.
    """

    def __contains__(self, arg0: int) -> bool: ...
    def __delitem__(self, arg0: int) -> None: ...
    def __getitem__(self, arg0: int) -> typing.Any: ...
    def __init__(
        self,
        array_shape: tuple[int, int, int],
        default_array: int | IndexArray3D | typing_extensions.Buffer,
    ) -> None: ...
    def __iter__(self) -> amulet.collections.Iterator: ...
    def __len__(self) -> int: ...
    def __setitem__(
        self, arg0: int, arg1: IndexArray3D | typing_extensions.Buffer
    ) -> None: ...
    def items(self) -> typing.Any: ...
    def keys(self) -> typing.Any: ...
    def populate(self, arg0: int) -> None: ...
    def values(self) -> typing.Any: ...
    @property
    def array_shape(self) -> tuple[int, int, int]: ...
    @property
    def default_array(self) -> int | numpy.ndarray: ...
    @default_array.setter
    def default_array(
        self, arg1: int | IndexArray3D | typing_extensions.Buffer
    ) -> None: ...
