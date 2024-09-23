from __future__ import annotations

import collections.abc
import types
import typing

import amulet.block
import amulet.collections
import amulet.palette.block_palette
import amulet.version
import numpy
import numpy.typing
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

    @typing.overload
    def __init__(self, shape: tuple[int, int, int]) -> None: ...
    @typing.overload
    def __init__(self, shape: tuple[int, int, int], value: int) -> None: ...
    @typing.overload
    def __init__(self, other: IndexArray3D) -> None: ...
    @typing.overload
    def __init__(self, arg0: typing_extensions.Buffer) -> None: ...
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
    def __getitem__(self, arg0: int) -> numpy.typing.NDArray[numpy.uint32]: ...
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
    def get(
        self, arg0: int, arg1: numpy.typing.NDArray[numpy.uint32] | None
    ) -> numpy.typing.NDArray[numpy.uint32] | None: ...
    def items(
        self,
    ) -> collections.abc.ItemsView[int, numpy.typing.NDArray[numpy.uint32]]: ...
    def keys(self) -> collections.abc.KeysView[int]: ...
    def pop(
        self, key: int, default: numpy.typing.NDArray[numpy.uint32] = ...
    ) -> numpy.typing.NDArray[numpy.uint32]: ...
    def popitem(self) -> tuple[int, numpy.typing.NDArray[numpy.uint32]]: ...
    def populate(self, arg0: int) -> None: ...
    def setdefault(
        self, arg0: int, arg1: numpy.typing.NDArray[numpy.uint32] | None
    ) -> numpy.typing.NDArray[numpy.uint32] | None: ...
    def update(self, other: typing.Any = (), **kwargs) -> None: ...
    def values(
        self,
    ) -> collections.abc.ValuesView[numpy.typing.NDArray[numpy.uint32]]: ...
    @property
    def array_shape(self) -> tuple[int, int, int]: ...
    @property
    def default_array(self) -> int | numpy.ndarray: ...
    @default_array.setter
    def default_array(
        self, arg1: int | IndexArray3D | typing_extensions.Buffer
    ) -> None: ...
