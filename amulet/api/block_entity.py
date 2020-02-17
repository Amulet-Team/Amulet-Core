from __future__ import annotations

import amulet_nbt
from .world_object import WorldObject


class BlockEntity(WorldObject):
    def __init__(
        self,
        namespace: str,
        base_name: str,
        x: int,
        y: int,
        z: int,
        nbt: amulet_nbt.NBTFile,
    ):
        self._namespace = namespace
        self._base_name = base_name
        self._namespaced_name = None
        self._gen_namespaced_name()
        self._x = x
        self._y = y
        self._z = z
        self._nbt = nbt

    def _gen_namespaced_name(self):
        self._namespaced_name = (
            "" if self.namespace in ["", None] else f"{self.namespace}:"
        ) + self.base_name

    def __repr__(self):
        return f"BlockEntity[{self.namespaced_name}, {self.x}, {self.y}, {self.z}]{{{self.nbt}}}"

    @property
    def namespaced_name(self) -> str:
        """
        The namespace:base_name of the block entity represented by the BlockEntity object (IE: `minecraft:creeper`)
        If the given namespace is an empty string it will just return the base name.
        :return: The namespace:base_name of the block entity or just base_name if no namespace
        """
        return self._namespaced_name

    @namespaced_name.setter
    def namespaced_name(self, value: str):
        self._namespaced_name = value
        if ":" in value:
            self._namespace, self._base_name = value.split(":", 1)
        else:
            self._namespace, self._base_name = None, value

    @property
    def namespace(self) -> str:
        """
        The namespace of the block entity represented by the BlockEntity object (IE: `minecraft`)
        :return: The namespace of the block entity
        """
        return self._namespace

    @namespace.setter
    def namespace(self, value: str):
        self._namespace = value
        self._gen_namespaced_name()

    @property
    def base_name(self) -> str:
        """
        The base name of the block entity represented by the BlockEntity object (IE: `creeper`, `pig`)
        :return: The base name of the block entity
        """
        return self._base_name

    @base_name.setter
    def base_name(self, value: str):
        self._base_name = value
        self._gen_namespaced_name()

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    @property
    def z(self) -> int:
        return self._z

    def new_at_location(self, x: int, y: int, z: int) -> BlockEntity:
        """Creates a copy of this BlockEntity at a new location
        BlockEntities are stored in the chunk based on their location so location cannot be mutable"""
        return BlockEntity(
            self._namespace,
            self._base_name,
            x,
            y,
            z,
            self._nbt  # TODO: should this be deepcopied?
        )

    @property
    def nbt(self) -> amulet_nbt.NBTFile:
        """
        The nbt behind the BlockEntity object
        :return: An amulet_nbt.NBTFile
        """
        return self._nbt

    @nbt.setter
    def nbt(self, value: str):
        self._nbt = value
