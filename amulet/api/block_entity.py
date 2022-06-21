from __future__ import annotations
import copy
import numpy

from amulet_nbt import NamedTag
from amulet.api.data_types import BlockCoordinates
from .abstract_base_entity import AbstractBaseEntity


class BlockEntity(AbstractBaseEntity):
    """
    A class to contain all the data to define a BlockEntity.
    """

    obj_name = "BlockEntity"
    coord_types = (int, numpy.integer)

    def __init__(
        self,
        namespace: str,
        base_name: str,
        x: int,
        y: int,
        z: int,
        nbt: NamedTag,
    ):
        """
        Constructs a :class:`BlockEntity` instance.

        :param namespace: The namespace of the block entity eg "minecraft"
        :param base_name: The base name of the block entity eg "chest"
        :param x: The x coordinate of the block entity
        :param y: The y coordinate of the block entity
        :param z: The z coordinate of the block entity
        :param nbt: The NBT stored with the block entity
        """
        super().__init__(namespace, base_name, x, y, z, nbt)

    @property
    def x(self) -> int:
        """The x location of the BlockEntity. Read Only"""
        return self._x

    @property
    def y(self) -> int:
        """The y location of the BlockEntity. Read Only"""
        return self._y

    @property
    def z(self) -> int:
        """The z location of the BlockEntity. Read Only"""
        return self._z

    @property
    def location(self) -> BlockCoordinates:
        """The location of the BlockEntity. Read Only"""
        return self._x, self._y, self._z

    def new_at_location(self, x: int, y: int, z: int) -> BlockEntity:
        """
        Creates a copy of this BlockEntity at a new location
        BlockEntities are stored in the chunk based on their location so location cannot be mutable
        """
        return BlockEntity(
            self._namespace,
            self._base_name,
            x,
            y,
            z,
            copy.deepcopy(self._nbt),
        )
