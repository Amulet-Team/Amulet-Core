from __future__ import annotations

import types
import typing

import amulet.block
import amulet.collections
import amulet.palette.block_palette
import amulet.version
import numpy
import typing_extensions

__all__ = ["BlockComponent", "BlockComponentData", "IndexArray3D", "SectionArrayMap"]

class BlockComponent:
    ComponentID: typing.ClassVar[str] = "Amulet::BlockComponent"
    block: BlockComponentData

class BlockComponentData:
    def __init__(
        self,
        version_range: amulet.version.VersionRange,
        array_shape: tuple[int, int, int],
        default_block: amulet.block.BlockStack,
    ) -> None: ...
    @property
    def palette(self) -> amulet.palette.block_palette.BlockPalette: ...
    @property
    def sections(self) -> SectionArrayMap: ...

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
    def __eq__(self, arg0: typing.Any) -> bool | types.NotImplementedType: ...
    def __getitem__(self, arg0: int) -> typing.Any: ...
    def __hash__(self) -> int: ...
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
    def get(self, arg0: typing.Any, arg1: typing.Any) -> typing.Any: ...
    def items(self) -> typing.Any: ...
    def keys(self) -> typing.Any: ...
    def pop(self, key: typing.Any, default: typing.Any = ...) -> typing.Any: ...
    def popitem(self) -> tuple[typing.Any, typing.Any]: ...
    def populate(self, arg0: int) -> None: ...
    def setdefault(self, arg0: typing.Any, arg1: typing.Any) -> typing.Any: ...
    def update(self, other: typing.Any = (), **kwargs) -> None: ...
    def values(self) -> typing.Any: ...
    @property
    def array_shape(self) -> tuple[int, int, int]: ...
    @property
    def default_array(self) -> int | numpy.ndarray: ...
    @default_array.setter
    def default_array(
        self, arg1: int | IndexArray3D | typing_extensions.Buffer
    ) -> None: ...
