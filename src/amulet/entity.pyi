from typing import Any

from amulet.data_types import PointCoordinates as PointCoordinates
from amulet.version import PlatformVersionContainer as PlatformVersionContainer
from amulet.version import VersionNumber as VersionNumber
from amulet_nbt import NamedTag

class Entity(PlatformVersionContainer):
    """
    A class to contain all the data to define an Entity.
    """

    def __init__(
        self,
        platform: str,
        version: VersionNumber,
        namespace: str,
        base_name: str,
        x: float,
        y: float,
        z: float,
        nbt: NamedTag,
    ) -> None:
        """
        Constructs a :class:`Entity` instance.

        :param platform: The platform the entity is defined in.
        :param version: The version the entity is defined in.
        :param namespace: The namespace of the entity eg "minecraft"
        :param base_name: The base name of the entity eg "creeper"
        :param x: The x coordinate of the entity
        :param y: The y coordinate of the entity
        :param z: The z coordinate of the entity
        :param nbt: The NBT stored with the entity
        """

    def __eq__(self, other: Any) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def namespaced_name(self) -> str:
        """
        The namespace:base_name of the entity represented by the object (eg: `minecraft:creeper`)

        If the given namespace is an empty string it will just return the base name.

        :return: namespace:base_name of the entity
        """

    @property
    def namespace(self) -> str:
        """
        The namespace of the entity represented by the Entity object (eg: `minecraft`)

        :return: The namespace of the entity
        """

    @namespace.setter
    def namespace(self, value: str) -> None: ...
    @property
    def base_name(self) -> str:
        """
        The base name of the entity represented by the Entity object (eg: `creeper`, `pig`)

        :return: The base name of the entity
        """

    @base_name.setter
    def base_name(self, value: str) -> None: ...
    @property
    def x(self) -> float:
        """The x location of the Entity."""

    @x.setter
    def x(self, value: float) -> None: ...
    @property
    def y(self) -> float:
        """The y location of the Entity."""

    @y.setter
    def y(self, value: float) -> None: ...
    @property
    def z(self) -> float:
        """The z location of the Entity."""

    @z.setter
    def z(self, value: float) -> None: ...
    @property
    def location(self) -> PointCoordinates:
        """The location of the Entity."""

    @location.setter
    def location(self, location: PointCoordinates) -> None: ...
    @property
    def nbt(self) -> NamedTag:
        """
        The NBT behind the object

        :getter: Get the NBT data stored in the object
        :setter: Set the NBT data stored in the object

        :return: A NamedTag
        """

    @nbt.setter
    def nbt(self, value: NamedTag) -> None: ...
