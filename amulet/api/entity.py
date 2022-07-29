from __future__ import annotations

import numpy
from typing import Tuple, Union
from amulet_nbt import NamedTag
from .abstract_base_entity import AbstractBaseEntity


class Entity(AbstractBaseEntity):
    """
    A class to contain all the data to define an Entity.
    """

    obj_name = "Entity"
    coord_types = (float, numpy.floating)

    def __init__(
        self,
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
        super().__init__(namespace, base_name, x, y, z, nbt)

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
    def location(self) -> Tuple[float, float, float]:
        """The location of the Entity."""
        return self._x, self._y, self._z

    @location.setter
    def location(
        self, location: Tuple[Union[int, float], Union[int, float], Union[int, float]]
    ):
        self._x, self._y, self._z = location
