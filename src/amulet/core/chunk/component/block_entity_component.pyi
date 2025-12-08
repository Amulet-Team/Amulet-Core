from __future__ import annotations

import collections.abc
import types
import typing

import amulet.core.block_entity
import amulet.core.version

__all__: list[str] = ["BlockEntityComponent", "BlockEntityStorage"]

class BlockEntityComponent:
    ComponentID: typing.ClassVar[str] = "Amulet::BlockEntityComponent"
    block_entities: BlockEntityStorage

class BlockEntityStorage:
    def __contains__(
        self, arg0: tuple[typing.SupportsInt, typing.SupportsInt, typing.SupportsInt]
    ) -> bool: ...
    def __delitem__(
        self, key: tuple[typing.SupportsInt, typing.SupportsInt, typing.SupportsInt]
    ) -> None: ...
    def __eq__(self, other: typing.Any) -> bool | types.NotImplementedType: ...
    def __getitem__(
        self, arg0: tuple[typing.SupportsInt, typing.SupportsInt, typing.SupportsInt]
    ) -> typing.Any: ...
    def __hash__(self) -> int: ...
    def __init__(
        self,
        version_range: amulet.core.version.VersionRange,
        x_size: typing.SupportsInt,
        z_size: typing.SupportsInt,
    ) -> None: ...
    def __iter__(self) -> collections.abc.Iterator[tuple[int, int, int]]: ...
    def __len__(self) -> int: ...
    def __repr__(self) -> str: ...
    def __setitem__(
        self,
        key: tuple[typing.SupportsInt, typing.SupportsInt, typing.SupportsInt],
        value: amulet.core.block_entity.BlockEntity,
    ) -> None: ...
    def clear(self) -> None: ...
    @typing.overload
    def get(
        self, key: tuple[typing.SupportsInt, typing.SupportsInt, typing.SupportsInt]
    ) -> amulet.core.block_entity.BlockEntity | None: ...
    @typing.overload
    def get(
        self,
        key: tuple[typing.SupportsInt, typing.SupportsInt, typing.SupportsInt],
        default: amulet.core.block_entity.BlockEntity,
    ) -> amulet.core.block_entity.BlockEntity: ...
    @typing.overload
    def get[T](
        self,
        key: tuple[typing.SupportsInt, typing.SupportsInt, typing.SupportsInt],
        default: T,
    ) -> amulet.core.block_entity.BlockEntity | T: ...
    def items(
        self,
    ) -> collections.abc.ItemsView[
        tuple[int, int, int], amulet.core.block_entity.BlockEntity
    ]: ...
    def keys(self) -> collections.abc.KeysView[tuple[int, int, int]]: ...
    @typing.overload
    def pop(
        self, key: tuple[typing.SupportsInt, typing.SupportsInt, typing.SupportsInt]
    ) -> amulet.core.block_entity.BlockEntity: ...
    @typing.overload
    def pop(
        self,
        key: tuple[typing.SupportsInt, typing.SupportsInt, typing.SupportsInt],
        default: amulet.core.block_entity.BlockEntity,
    ) -> amulet.core.block_entity.BlockEntity: ...
    @typing.overload
    def pop[T](
        self,
        key: tuple[typing.SupportsInt, typing.SupportsInt, typing.SupportsInt],
        default: T,
    ) -> amulet.core.block_entity.BlockEntity | T: ...
    def popitem(
        self,
    ) -> tuple[tuple[int, int, int], amulet.core.block_entity.BlockEntity]: ...
    @typing.overload
    def setdefault(
        self, key: tuple[typing.SupportsInt, typing.SupportsInt, typing.SupportsInt]
    ) -> amulet.core.block_entity.BlockEntity: ...
    @typing.overload
    def setdefault(
        self,
        key: tuple[typing.SupportsInt, typing.SupportsInt, typing.SupportsInt],
        default: amulet.core.block_entity.BlockEntity,
    ) -> amulet.core.block_entity.BlockEntity: ...
    def update(
        self,
        other: (
            collections.abc.Mapping[
                tuple[int, int, int], amulet.core.block_entity.BlockEntity
            ]
            | collections.abc.Iterable[
                tuple[tuple[int, int, int], amulet.core.block_entity.BlockEntity]
            ]
        ) = (),
        **kwargs: amulet.core.block_entity.BlockEntity,
    ) -> None: ...
    def values(
        self,
    ) -> collections.abc.ValuesView[amulet.core.block_entity.BlockEntity]: ...
    @property
    def x_size(self) -> int: ...
    @property
    def z_size(self) -> int: ...
