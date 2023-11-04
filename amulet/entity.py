from __future__ import annotations

from typing import Tuple, Union
from amulet_nbt import NamedTag
from amulet.version import AbstractVersion, VersionContainer
from amulet.api.data_types import PointCoordinates


class Entity(VersionContainer):
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
        version: AbstractVersion,
        namespace: str,
        base_name: str,
        x: float,
        y: float,
        z: float,
        nbt: NamedTag,
    ):
        """
        Constructs a :class:`Entity` instance.

        :param namespace: The namespace of the entity eg "minecraft"
        :param base_name: The base name of the entity eg "creeper"
        :param x: The x coordinate of the entity
        :param y: The y coordinate of the entity
        :param z: The z coordinate of the entity
        :param nbt: The NBT stored with the entity
        """
        super().__init__(version)
        self._namespace = str(namespace)
        self._base_name = str(base_name)
        self._x = float(x)
        self._y = float(y)
        self._z = float(z)
        if not isinstance(nbt, NamedTag):
            raise TypeError(f"nbt must be an NamedTag. Got {nbt}")
        self._nbt = nbt

    def _data(self):
        return (
            self.version,
            self._namespace,
            self._base_name,
            self._x,
            self._y,
            self._z,
            self._nbt,
        )

    def __eq__(self, other):
        if not isinstance(other, Entity):
            return NotImplemented
        return self._data() == other._data()

    def __hash__(self):
        return id(self)

    def __repr__(self):
        return f"Entity({self.version!r}, {self._namespace!r}, {self._base_name!r}, {self._x}, {self._y}, {self._z}, {self._nbt!r})"

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
    def namespace(self, value: str):
        self._namespace = value

    @property
    def base_name(self) -> str:
        """
        The base name of the entity represented by the Entity object (eg: `creeper`, `pig`)

        :return: The base name of the entity
        """
        return self._base_name

    @base_name.setter
    def base_name(self, value: str):
        self._base_name = value

    @property
    def x(self) -> float:
        """The x location of the Entity."""
        return self._x

    @x.setter
    def x(self, value: float):
        self._x = value

    @property
    def y(self) -> float:
        """The y location of the Entity."""
        return self._y

    @y.setter
    def y(self, value: float):
        self._y = value

    @property
    def z(self) -> float:
        """The z location of the Entity."""
        return self._z

    @z.setter
    def z(self, value: float):
        self._z = value

    @property
    def location(self) -> PointCoordinates:
        """The location of the Entity."""
        return self._x, self._y, self._z

    @location.setter
    def location(
        self, location: Tuple[Union[int, float], Union[int, float], Union[int, float]]
    ):
        self._x, self._y, self._z = location

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
    def nbt(self, value: NamedTag):
        if not isinstance(value, NamedTag):
            raise TypeError
        self._nbt = value
