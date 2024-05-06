from __future__ import annotations

from typing import TYPE_CHECKING
from abc import ABC, abstractmethod

from amulet.version import VersionNumber

if TYPE_CHECKING:
    from .block import BlockData
    from .biome import BiomeData


class GameVersion(ABC):
    @abstractmethod
    def supports_version(self, platform: str, version: VersionNumber) -> bool:
        raise NotImplementedError

    @property
    @abstractmethod
    def platform(self) -> str:
        """The platform string this instance is part of."""
        raise NotImplementedError

    @property
    @abstractmethod
    def min_version(self) -> VersionNumber:
        """The minimum game version this instance can be used with."""
        raise NotImplementedError

    @property
    @abstractmethod
    def max_version(self) -> VersionNumber:
        """The maximum game version this instance can be used with."""
        raise NotImplementedError

    @property
    @abstractmethod
    def block(self) -> BlockData:
        raise NotImplementedError

    @property
    @abstractmethod
    def biome(self) -> BiomeData:
        raise NotImplementedError
