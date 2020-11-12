from __future__ import annotations
from typing import Tuple
import copy
import numpy

import amulet_nbt
from .entity_base_object import EntityObject


class BlockEntity(EntityObject):
    obj_name = "BlockEntity"
    coord_types = (int, numpy.integer)

    def __init__(
        self,
        namespace: str,
        base_name: str,
        x: int,
        y: int,
        z: int,
        nbt: amulet_nbt.NBTFile,
    ):
        super().__init__(namespace, base_name, x, y, z, nbt)

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    @property
    def z(self) -> int:
        return self._z

    @property
    def location(self) -> Tuple[int, int, int]:
        return self._x, self._y, self._z

    def new_at_location(self, x: int, y: int, z: int) -> BlockEntity:
        """Creates a copy of this BlockEntity at a new location
        BlockEntities are stored in the chunk based on their location so location cannot be mutable"""
        return BlockEntity(
            self._namespace,
            self._base_name,
            x,
            y,
            z,
            copy.deepcopy(self._nbt),
        )
