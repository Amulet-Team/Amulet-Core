from __future__ import annotations

from typing import Union, Tuple, Optional
import amulet_nbt

_Coord = Union[float, int]


class EntityObject:
    obj_name = "Unknown"
    coord_types: Optional[tuple] = None

    def __init__(
        self,
        namespace: str,
        base_name: str,
        x: _Coord,
        y: _Coord,
        z: _Coord,
        nbt: amulet_nbt.NBTFile,
    ):
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
        if isinstance(nbt, amulet_nbt.TAG_Compound):
            self._nbt = amulet_nbt.NBTFile(nbt)
        elif isinstance(nbt, amulet_nbt.NBTFile):
            self._nbt = nbt
        else:
            raise Exception(f"nbt must be an NBTFile. Got {nbt}")

    def _gen_namespaced_name(self):
        self._namespaced_name = f'{self.namespace or ""}:{self.base_name}'

    def __repr__(self):
        return f"{self.obj_name}[{self.namespaced_name}, {self.x}, {self.y}, {self.z}]{{{self.nbt}}}"

    @property
    def namespaced_name(self) -> str:
        """
        The namespace:base_name of the entity represented by the object (IE: `minecraft:creeper`)
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
    def x(self) -> _Coord:
        return self._x

    @property
    def y(self) -> _Coord:
        return self._y

    @property
    def z(self) -> _Coord:
        return self._z

    @property
    def location(self) -> Union[Tuple[int, int, int], Tuple[float, float, float]]:
        return self._x, self._y, self._z

    @property
    def nbt(self) -> amulet_nbt.NBTFile:
        """
        The nbt behind the BlockEntity object

        :return: An amulet_nbt.NBTFile
        """
        return self._nbt

    @nbt.setter
    def nbt(self, value: amulet_nbt.NBTFile):
        self._nbt = value
