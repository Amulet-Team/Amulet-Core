from _typeshed import Incomplete
from amulet.version import AbstractVersion as AbstractVersion, VersionContainer as VersionContainer
from amulet_nbt import NamedTag

class BlockEntity(VersionContainer):
    """
    A class to contain all the data to define a BlockEntity.
    """
    __slots__: Incomplete
    _namespace: Incomplete
    _base_name: Incomplete
    _nbt: Incomplete
    def __init__(self, version: AbstractVersion, namespace: str, base_name: str, nbt: NamedTag) -> None:
        '''
        Constructs a :class:`BlockEntity` instance.

        :param namespace: The namespace of the block entity eg "minecraft"
        :param base_name: The base name of the block entity eg "chest"
        :param nbt: The NBT stored with the block entity
        '''
    def __repr__(self) -> str: ...
    def _data(self): ...
    def __eq__(self, other): ...
    @property
    def namespaced_name(self) -> str:
        """
        The namespace:base_name of the entity represented by the object (eg: `minecraft:chest`)

        If the given namespace is an empty string it will just return the base name.

        :return: The namespace:base_name of the block entity
        """
    @property
    def namespace(self) -> str:
        """
        The namespace of the block entity represented by the BlockEntity object (eg: `minecraft`)

        :return: The namespace of the block entity
        """
    @namespace.setter
    def namespace(self, value: str): ...
    @property
    def base_name(self) -> str:
        """
        The base name of the block entity represented by the BlockEntity object (eg: `chest`, `furnace`)

        :return: The base name of the block entity
        """
    @base_name.setter
    def base_name(self, value: str): ...
    @property
    def nbt(self) -> NamedTag:
        """
        The NBT behind the object

        :getter: Get the NBT data stored in the object
        :setter: Set the NBT data stored in the object

        :return: A NamedTag
        """
    @nbt.setter
    def nbt(self, value: NamedTag): ...
