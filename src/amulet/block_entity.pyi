from __future__ import annotations

import types
import typing

import amulet.version
import amulet_nbt

__all__ = ["BlockEntity"]

class BlockEntity(amulet.version.PlatformVersionContainer):
    """
    A class to contain all the data to define a BlockEntity.
    """

    @typing.overload
    def __eq__(self, arg0: BlockEntity) -> bool: ...
    @typing.overload
    def __eq__(self, arg0: typing.Any) -> bool | types.NotImplementedType: ...
    def __getstate__(self) -> bytes: ...
    def __hash__(self) -> int: ...
    def __init__(
        self,
        platform: str,
        version: amulet.version.VersionNumber,
        namespace: str,
        base_name: str,
        nbt: amulet_nbt.NamedTag,
    ) -> None: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, arg0: bytes) -> None: ...
    @property
    def base_name(self) -> str:
        """
        The base name of the block entity represented by the :class:`BlockEntity` object.

        >>> block_entity: BlockEntity
        >>> block_entity.base_name

        :return: The base name of the block entity
        """

    @base_name.setter
    def base_name(self, arg1: str) -> None: ...
    @property
    def namespace(self) -> str:
        """
        The namespace of the block entity represented by the :class:`BlockEntity` object.

        >>> block_entity: BlockEntity
        >>> block_entity.namespace

        :return: The namespace of the block entity
        """

    @namespace.setter
    def namespace(self, arg1: str) -> None: ...
    @property
    def namespaced_name(self) -> str:
        """
        The namespace:base_name of the block entity represented by the :class:`BlockEntity` object.

        >>> block_entity: BlockEntity
        >>> block_entity.namespaced_name

        :return: The namespace:base_name of the block entity
        """

    @property
    def nbt(self) -> amulet_nbt.NamedTag:
        """
        The nbt data for the block entity.
        >>> block_entity: BlockEntity
        >>> block_entity.nbt

        :return: The NamedTag of the block entity
        """

    @nbt.setter
    def nbt(self, arg1: amulet_nbt.NamedTag) -> None: ...
