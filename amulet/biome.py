from __future__ import annotations
from typing import Any

from amulet.version import PlatformVersionContainer, VersionNumber


class Biome(PlatformVersionContainer):
    def __init__(
        self,
        platform: str,
        version: VersionNumber,
        namespace: str,
        base_name: str,
    ):
        """
        Constructs a :class:`Biome` instance.

        >>> plains = Biome("java", VersionNumber(3700), "minecraft", "plains")

        :param version: The platform and version the entity is defined in.
        :param namespace: The string namespace of the biome. eg `minecraft`
        :param base_name: The string base name of the biome. eg `plains`
        """
        super().__init__(platform, version)
        self._namespace = str(namespace)
        self._base_name = str(base_name)

    def __getstate__(self) -> tuple[Any, ...]:
        return *super().__getstate__(), self._namespace, self._base_name

    def __setstate__(self, state: tuple[Any, ...]) -> tuple[Any, ...]:
        self._namespace, self._base_name, *state = super().__setstate__(state)
        return state

    def __hash__(self) -> int:
        return hash(self.__getstate__())

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Biome):
            return NotImplemented
        return self.__getstate__() == other.__getstate__()

    def __gt__(self, other: Biome) -> bool:
        if not isinstance(other, Biome):
            return NotImplemented
        return hash(self) > hash(other)

    def __lt__(self, other: Biome) -> bool:
        if not isinstance(other, Biome):
            return NotImplemented
        return hash(self) < hash(other)

    def __repr__(self) -> str:
        return f"Biome({self.platform!r}, {self.version!r}, {self.namespace!r}, {self.base_name!r}, {self.version!r})"

    @property
    def namespaced_name(self) -> str:
        """
        The namespace:base_name of the biome represented by the :class:`Biome` object.

        >>> plains = Biome("java", VersionNumber(3837), "minecraft", "plains")
        >>> plains.namespaced_name
        'minecraft:plains'

        :return: The namespace:base_name of the biome
        """
        return f"{self.namespace}:{self.base_name}"

    @property
    def namespace(self) -> str:
        """
        The namespace of the biome represented by the :class:`Biome` object.

        >>> plains = Biome("bedrock", VersionNumber(1, 20, 61), "minecraft", "plains")
        >>> plains.namespace
        "minecraft"

        :return: The namespace of the biome
        """
        return self._namespace

    @property
    def base_name(self) -> str:
        """
        The base name of the biome represented by the :class:`Biome` object.

        >>> plains = Biome("bedrock", VersionNumber(1, 20, 61), "minecraft", "plains")
        >>> plains.base_name
        "plains"

        :return: The base name of the biome
        """
        return self._base_name
