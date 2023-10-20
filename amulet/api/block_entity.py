from __future__ import annotations
import copy

from amulet_nbt import NamedTag
from amulet.api.data_types import BlockCoordinates


class BlockEntity:
    """
    A class to contain all the data to define a BlockEntity.
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
        self._namespace = str(namespace)
        self._base_name = str(base_name)
        self._x = int(x)
        self._y = int(y)
        self._z = int(z)
        if not isinstance(nbt, NamedTag):
            raise TypeError(f"nbt must be an NamedTag. Got {nbt}")
        self._nbt = nbt

    def __repr__(self):
        return f"BlockEntity({self._namespace!r}, {self._base_name!r}, {self._x}, {self._y}, {self._z}, {self._nbt!r})"

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

    @property
    def namespaced_name(self) -> str:
        """
        The namespace:base_name of the entity represented by the object (eg: `minecraft:chest`)

        If the given namespace is an empty string it will just return the base name.

        :return: The namespace:base_name of the block entity
        """
        return f"{self._namespace}:{self._base_name}"

    @property
    def namespace(self) -> str:
        """
        The namespace of the block entity represented by the BlockEntity object (eg: `minecraft`)

        :return: The namespace of the block entity
        """
        return self._namespace

    @namespace.setter
    def namespace(self, value: str):
        self._namespace = value

    @property
    def base_name(self) -> str:
        """
        The base name of the block entity represented by the BlockEntity object (eg: `chest`, `furnace`)

        :return: The base name of the block entity
        """
        return self._base_name

    @base_name.setter
    def base_name(self, value: str):
        self._base_name = value

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
    def location(self) -> BlockCoordinates:
        return self._x, self._y, self._z

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
