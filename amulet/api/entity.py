from __future__ import annotations

import numpy
from typing import Tuple, Union
import amulet_nbt
from .entity_base_object import EntityObject


class Entity(EntityObject):
    obj_name = "Entity"
    coord_types = (float, numpy.floating)

    def __init__(
        self,
        namespace: str,
        base_name: str,
        x: float,
        y: float,
        z: float,
        nbt: amulet_nbt.NBTFile,
    ):
        super().__init__(namespace, base_name, x, y, z, nbt)

    @property
    def x(self) -> float:
        return self._x

    @x.setter
    def x(self, value: float):
        self._x = value

    @property
    def y(self) -> float:
        return self._y

    @y.setter
    def y(self, value: float):
        self._y = value

    @property
    def z(self) -> float:
        return self._z

    @z.setter
    def z(self, value: float):
        self._z = value

    @property
    def location(self) -> Tuple[float, float, float]:
        return self._x, self._y, self._z

    @location.setter
    def location(
        self, location: Tuple[Union[int, float], Union[int, float], Union[int, float]]
    ):
        self._x, self._y, self._z = location
