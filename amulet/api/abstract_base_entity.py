from __future__ import annotations

from abc import ABC
from typing import Union, Optional
from amulet_nbt import NamedTag, CompoundTag
from amulet.api.data_types import BlockCoordinates, PointCoordinates

_Coord = Union[float, int]


class AbstractBaseEntity(ABC):
    obj_name: str = None
    coord_types: Optional[tuple] = None

    def __init__(
        self,
        namespace: str,
        base_name: str,
        x: _Coord,
        y: _Coord,
        z: _Coord,
        nbt: NamedTag,
    ):
        assert isinstance(self.obj_name, str)
        assert self.coord_types is not None
        assert isinstance(namespace, str), "namespace must be a string"
        assert isinstance(base_name, str), "base_name must be a string"
        self._namespace = namespace
        self._base_name = base_name
        self._namespaced_name = None
        self._gen_namespaced_name()
        assert all(
            isinstance(c, self.coord_types) for c in (x, y, z)
        ), f"coordinates type must be in {self.coord_types}"
        self._x = self.coord_types[0](x)
        self._y = self.coord_types[0](y)
        self._z = self.coord_types[0](z)
        if isinstance(nbt, CompoundTag):
            self._nbt = NamedTag(nbt)
        elif isinstance(nbt, NamedTag):
            self._nbt = nbt
        else:
            raise Exception(f"nbt must be an NamedTag. Got {nbt}")

    def _gen_namespaced_name(self):
        self._namespaced_name = f'{self.namespace or ""}:{self.base_name}'

    def __repr__(self):
        return f"{self.obj_name}[{self.namespaced_name}, {self.x}, {self.y}, {self.z}]{{{self.nbt}}}"

    @property
    def namespaced_name(self) -> str:
        """
        The namespace:base_name of the entity represented by the object (eg: `minecraft:creeper`)

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
            self._namespace, self._base_name = "", value

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
        self._gen_namespaced_name()

    @property
    def base_name(self) -> str:
        """
        The base name of the block entity represented by the BlockEntity object (eg: `creeper`, `pig`)

        :return: The base name of the block entity
        """
        return self._base_name

    @base_name.setter
    def base_name(self, value: str):
        self._base_name = value
        self._gen_namespaced_name()

    @property
    def x(self) -> _Coord:
        return self._x

    @property
    def y(self) -> _Coord:
        return self._y

    @property
    def z(self) -> _Coord:
        return self._z

    @property
    def location(self) -> Union[BlockCoordinates, PointCoordinates]:
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
