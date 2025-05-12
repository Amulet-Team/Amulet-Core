from __future__ import annotations

import types
import typing

import amulet.core.version

__all__ = ["Biome"]

class Biome(amulet.core.version.PlatformVersionContainer):
    """
    A class to manage the state of a biome.

    It is an immutable object that contains the platform, version, namespace and base name.

    Here's a few examples on how create a Biome object:

    >>> # Create a plains biome for Java 1.20.2
    >>> plains = Biome("java", VersionNumber(3578), "minecraft", "plains")
    >>> # The version number for Java is the Java data version

    >>> # Create a plains biome for Bedrock
    >>> plains = Biome("bedrock", VersionNumber(1, 21, 0, 3), "minecraft", "plains")
    >>> # The biome version number is unused in Bedrock but it is here for completeness.
    """

    @typing.overload
    def __eq__(self, arg0: Biome) -> bool: ...
    @typing.overload
    def __eq__(self, arg0: typing.Any) -> bool | types.NotImplementedType: ...
    def __ge__(self, arg0: Biome) -> bool: ...
    def __gt__(self, arg0: Biome) -> bool: ...
    def __hash__(self) -> int: ...
    def __init__(
        self,
        platform: str,
        version: amulet.core.version.VersionNumber,
        namespace: str,
        base_name: str,
    ) -> None: ...
    def __le__(self, arg0: Biome) -> bool: ...
    def __lt__(self, arg0: Biome) -> bool: ...
    def __repr__(self) -> str: ...
    @property
    def base_name(self) -> str:
        """
        The base name of the :class:`Biome` object.

        >>> biome: Biome
        >>> biome.base_name

        :return: The base name of the biome
        """

    @property
    def namespace(self) -> str:
        """
        The namespace of the :class:`Biome` object.

        >>> biome: Biome
        >>> water.namespace

        :return: The namespace of the biome
        """

    @property
    def namespaced_name(self) -> str:
        """
        The namespaced id of the :class:`Biome` object.

        >>> biome: Biome
        >>> biome.namespaced_name

        :return: The "namespace:base_name" of the biome
        """
