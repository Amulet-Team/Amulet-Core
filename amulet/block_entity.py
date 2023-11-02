from __future__ import annotations

from amulet_nbt import NamedTag
from amulet.game_version import AbstractGameVersion, GameVersionContainer


class BlockEntity(GameVersionContainer):
    """
    A class to contain all the data to define a BlockEntity.
    """

    __slots__ = (
        "_namespace",
        "_base_name",
        "_nbt",
    )

    def __init__(
        self,
        version: AbstractGameVersion,
        namespace: str,
        base_name: str,
        nbt: NamedTag,
    ):
        """
        Constructs a :class:`BlockEntity` instance.

        :param namespace: The namespace of the block entity eg "minecraft"
        :param base_name: The base name of the block entity eg "chest"
        :param nbt: The NBT stored with the block entity
        """
        super().__init__(version)
        self._namespace = str(namespace)
        self._base_name = str(base_name)
        if not isinstance(nbt, NamedTag):
            raise TypeError(f"nbt must be an NamedTag. Got {nbt}")
        self._nbt = nbt

    def __repr__(self):
        return f"BlockEntity({self.version}, {self._namespace!r}, {self._base_name!r}, {self._nbt!r})"

    def _data(self):
        return self.version, self._namespace, self._base_name, self._nbt

    def __eq__(self, other):
        if not isinstance(other, BlockEntity):
            return NotImplemented
        return self._data() == other._data()

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
