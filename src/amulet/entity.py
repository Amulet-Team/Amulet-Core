from __future__ import annotations

from typing import Any
from amulet_nbt import NamedTag
from amulet.version import PlatformVersionContainer, VersionNumber
from amulet.data_types import PointCoordinates


class Entity(PlatformVersionContainer):
    """
    A class to contain all the data to define an Entity.
    """

    __slots__ = (
        "_namespace",
        "_base_name",
        "_x",
        "_y",
        "_z",
        "_nbt",
    )

    def __init__(
        self,
        platform: str,
        version: VersionNumber,
        namespace: str,
        base_name: str,
        x: float,
        y: float,
        z: float,
        nbt: NamedTag,
    ) -> None:
        """
        Constructs a :class:`Entity` instance.

        :param platform: The platform the entity is defined in.
        :param version: The version the entity is defined in.
        :param namespace: The namespace of the entity eg "minecraft"
        :param base_name: The base name of the entity eg "creeper"
        :param x: The x coordinate of the entity
        :param y: The y coordinate of the entity
        :param z: The z coordinate of the entity
        :param nbt: The NBT stored with the entity
        """
        super().__init__(platform, version)
        self._namespace = str(namespace)
        self._base_name = str(base_name)
        self._x = float(x)
        self._y = float(y)
        self._z = float(z)
        if not isinstance(nbt, NamedTag):
            raise TypeError(f"nbt must be an NamedTag. Got {nbt}")
        self._nbt = nbt

    def __getstate__(self) -> tuple[tuple[str, VersionNumber], tuple[str, str, float, float, float, NamedTag]]:  # type: ignore[override]
        return (
            super().__getstate__(),
            (
                self._namespace,
                self._base_name,
                self._x,
                self._y,
                self._z,
                self._nbt,
            ),
        )

    def __setstate__(self, state: tuple[tuple[str, VersionNumber], tuple[str, str, float, float, float, NamedTag]]) -> None:  # type: ignore[override]
        super().__setstate__(state[0])
        (
            self._namespace,
            self._base_name,
            self._x,
            self._y,
            self._z,
            self._nbt,
        ) = state[1]

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Entity):
            return NotImplemented
        return self.__getstate__() == other.__getstate__()

    def __hash__(self) -> int:
        return id(self)

    def __repr__(self) -> str:
        return f"Entity({self.platform!r}, {self.version!r}, {self._namespace!r}, {self._base_name!r}, {self._x}, {self._y}, {self._z}, {self._nbt!r})"

    @property
    def namespaced_name(self) -> str:
        """
        The namespace:base_name of the entity represented by the object (eg: `minecraft:creeper`)

        If the given namespace is an empty string it will just return the base name.

        :return: namespace:base_name of the entity
        """
        return f"{self._namespace}:{self._base_name}"

    @property
    def namespace(self) -> str:
        """
        The namespace of the entity represented by the Entity object (eg: `minecraft`)

        :return: The namespace of the entity
        """
        return self._namespace

    @namespace.setter
    def namespace(self, value: str) -> None:
        self._namespace = value

    @property
    def base_name(self) -> str:
        """
        The base name of the entity represented by the Entity object (eg: `creeper`, `pig`)

        :return: The base name of the entity
        """
        return self._base_name

    @base_name.setter
    def base_name(self, value: str) -> None:
        self._base_name = value

    @property
    def x(self) -> float:
        """The x location of the Entity."""
        return self._x

    @x.setter
    def x(self, value: float) -> None:
        self._x = float(value)

    @property
    def y(self) -> float:
        """The y location of the Entity."""
        return self._y

    @y.setter
    def y(self, value: float) -> None:
        self._y = float(value)

    @property
    def z(self) -> float:
        """The z location of the Entity."""
        return self._z

    @z.setter
    def z(self, value: float) -> None:
        self._z = float(value)

    @property
    def location(self) -> PointCoordinates:
        """The location of the Entity."""
        return self._x, self._y, self._z

    @location.setter
    def location(self, location: PointCoordinates) -> None:
        self.x, self.y, self.z = location

    @property
    def nbt(self) -> NamedTag:
        """
        The NBT behind the object

        :getter: Get the NBT data stored in the object
        :setter: Set the NBT data stored in the object

        :return: A NamedTag
        """
        return self._nbt

    @nbt.setter
    def nbt(self, value: NamedTag) -> None:
        if not isinstance(value, NamedTag):
            raise TypeError
        self._nbt = value
