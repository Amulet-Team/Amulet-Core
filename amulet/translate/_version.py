from __future__ import annotations

from abc import ABC, abstractmethod

from amulet.version import VersionNumber


class Version(ABC):
    @abstractmethod
    def supports_version(self, platform: str, version: VersionNumber) -> bool:
        raise NotImplementedError

    @property
    @abstractmethod
    def platform(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def min_version(self) -> VersionNumber:
        raise NotImplementedError

    @property
    @abstractmethod
    def max_version(self) -> VersionNumber:
        raise NotImplementedError
