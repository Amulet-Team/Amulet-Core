from __future__ import annotations

from abc import abstractmethod

from amulet.version import VersionT
from ._level import Level, LevelPrivateT, RawLevelT, DimensionT


class DiskLevel(Level[LevelPrivateT, DimensionT, VersionT, RawLevelT]):
    """A level base class for all levels with data on disk."""

    __slots__ = ()

    @property
    @abstractmethod
    def path(self) -> str:
        """The path to the level on disk."""
        raise NotImplementedError
