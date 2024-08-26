from __future__ import annotations
import typing
import typing_extensions

__all__ = ["IndexArray3D"]

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
