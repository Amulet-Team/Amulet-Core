from __future__ import annotations

import types
import typing

import amulet.core.version
import amulet.nbt

__all__ = ["Entity"]

class Entity(amulet.core.version.PlatformVersionContainer):
    """
    A class to contain all the data to define an Entity.
    """

    @typing.overload
    def __eq__(self, arg0: Entity) -> bool: ...
    @typing.overload
    def __eq__(self, arg0: typing.Any) -> bool | types.NotImplementedType: ...
    def __hash__(self) -> int: ...
    def __init__(
        self,
        platform: str,
        version: amulet.core.version.VersionNumber,
        namespace: str,
        base_name: str,
        x: float,
        y: float,
        z: float,
        nbt: amulet.nbt.NamedTag,
    ) -> None: ...
    def __repr__(self) -> str: ...
    @property
    def base_name(self) -> str:
        """
        The base name of the entity represented by the :class:`Entity` object.

        >>> entity: Entity
        >>> entity.base_name

        :return: The base name of the entity
        """

    @base_name.setter
    def base_name(self, arg1: str) -> None: ...
    @property
    def namespace(self) -> str:
        """
        The namespace of the entity represented by the :class:`Entity` object.

        >>> entity: Entity
        >>> entity.namespace

        :return: The namespace of the entity
        """

    @namespace.setter
    def namespace(self, arg1: str) -> None: ...
    @property
    def namespaced_name(self) -> str:
        """
        The namespace:base_name of the entity represented by the :class:`Entity` object.

        >>> entity: Entity
        >>> entity.namespaced_name

        :return: The namespace:base_name of the entity
        """

    @property
    def nbt(self) -> amulet.nbt.NamedTag:
        """
        The nbt data for the entity.
        >>> entity: Entity
        >>> entity.nbt

        :return: The NamedTag of the entity
        """

    @nbt.setter
    def nbt(self, arg1: amulet.nbt.NamedTag) -> None: ...
    @property
    def x(self) -> float:
        """
        The x coordinate of the entity.
        """

    @x.setter
    def x(self, arg1: float) -> None: ...
    @property
    def y(self) -> float:
        """
        The y coordinate of the entity.
        """

    @y.setter
    def y(self, arg1: float) -> None: ...
    @property
    def z(self) -> float:
        """
        The z coordinate of the entity.
        """

    @z.setter
    def z(self, arg1: float) -> None: ...
