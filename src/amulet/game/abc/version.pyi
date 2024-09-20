import abc
from abc import ABC, abstractmethod

from amulet.version import VersionNumber as VersionNumber

from .biome import BiomeData as BiomeData
from .block import BlockData as BlockData

class GameVersion(ABC, metaclass=abc.ABCMeta):
    @abstractmethod
    def supports_version(self, platform: str, version: VersionNumber) -> bool: ...
    @property
    @abstractmethod
    def platform(self) -> str:
        """The platform string this instance is part of."""

    @property
    @abstractmethod
    def min_version(self) -> VersionNumber:
        """The minimum game version this instance can be used with."""

    @property
    @abstractmethod
    def max_version(self) -> VersionNumber:
        """The maximum game version this instance can be used with."""

    @property
    @abstractmethod
    def block(self) -> BlockData: ...
    @property
    @abstractmethod
    def biome(self) -> BiomeData: ...
