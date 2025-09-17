from __future__ import annotations

import collections.abc
import types
import typing

import numpy
import numpy.typing

__all__: list[str] = ["IndexArray3D", "SectionArrayMap"]

class IndexArray3D:
    """
    A 3D index array.
    """

    @typing.overload
    def __init__(
        self, shape: tuple[typing.SupportsInt, typing.SupportsInt, typing.SupportsInt]
    ) -> None: ...
    @typing.overload
    def __init__(
        self,
        shape: tuple[typing.SupportsInt, typing.SupportsInt, typing.SupportsInt],
        value: typing.SupportsInt,
    ) -> None: ...
    @typing.overload
    def __init__(self, other: IndexArray3D) -> None: ...
    @typing.overload
    def __init__(self, arg0: collections.abc.Buffer) -> None: ...
    @property
    def shape(self) -> tuple[int, int, int]: ...
    @property
    def size(self) -> int: ...

class SectionArrayMap:
    """
    A container of sub-chunk arrays.
    """

    def __contains__(self, arg0: typing.SupportsInt) -> bool: ...
    def __delitem__(self, arg0: typing.SupportsInt) -> None: ...
    def __eq__(self, other: typing.Any) -> bool | types.NotImplementedType: ...
    def __getitem__(
        self, arg0: typing.SupportsInt
    ) -> numpy.typing.NDArray[numpy.uint32]: ...
    def __hash__(self) -> int: ...
    def __init__(
        self,
        array_shape: tuple[typing.SupportsInt, typing.SupportsInt, typing.SupportsInt],
        default_array: typing.SupportsInt | IndexArray3D | collections.abc.Buffer,
    ) -> None: ...
    def __iter__(self) -> collections.abc.Iterator[int]: ...
    def __len__(self) -> int: ...
    def __setitem__(
        self, arg0: typing.SupportsInt, arg1: IndexArray3D | collections.abc.Buffer
    ) -> None: ...
    @typing.overload
    def get(
        self, key: typing.SupportsInt
    ) -> numpy.typing.NDArray[numpy.uint32] | None: ...
    @typing.overload
    def get(
        self, key: typing.SupportsInt, default: numpy.typing.NDArray[numpy.uint32]
    ) -> numpy.typing.NDArray[numpy.uint32]: ...
    @typing.overload
    def get[T](
        self, key: typing.SupportsInt, default: T
    ) -> numpy.typing.NDArray[numpy.uint32] | T: ...
    def items(
        self,
    ) -> collections.abc.ItemsView[int, numpy.typing.NDArray[numpy.uint32]]: ...
    def keys(self) -> collections.abc.KeysView[int]: ...
    @typing.overload
    def pop(self, key: typing.SupportsInt) -> numpy.typing.NDArray[numpy.uint32]: ...
    @typing.overload
    def pop(
        self, key: typing.SupportsInt, default: numpy.typing.NDArray[numpy.uint32]
    ) -> numpy.typing.NDArray[numpy.uint32]: ...
    @typing.overload
    def pop[T](
        self, key: typing.SupportsInt, default: T
    ) -> numpy.typing.NDArray[numpy.uint32] | T: ...
    def popitem(self) -> tuple[int, numpy.typing.NDArray[numpy.uint32]]: ...
    def populate(self, arg0: typing.SupportsInt) -> None: ...
    @typing.overload
    def setdefault(
        self, key: typing.SupportsInt
    ) -> numpy.typing.NDArray[numpy.uint32]: ...
    @typing.overload
    def setdefault(
        self, key: typing.SupportsInt, default: numpy.typing.NDArray[numpy.uint32]
    ) -> numpy.typing.NDArray[numpy.uint32]: ...
    def update(
        self,
        other: (
            collections.abc.Mapping[
                typing.SupportsInt, numpy.typing.NDArray[numpy.uint32]
            ]
            | collections.abc.Iterable[
                tuple[typing.SupportsInt, numpy.typing.NDArray[numpy.uint32]]
            ]
        ) = (),
        **kwargs: numpy.typing.NDArray[numpy.uint32],
    ) -> None: ...
    def values(
        self,
    ) -> collections.abc.ValuesView[numpy.typing.NDArray[numpy.uint32]]: ...
    @property
    def array_shape(self) -> tuple[int, int, int]: ...
    @property
    def default_array(self) -> int | numpy.ndarray: ...
    @default_array.setter
    def default_array(
        self, arg1: typing.SupportsInt | IndexArray3D | collections.abc.Buffer
    ) -> None: ...
