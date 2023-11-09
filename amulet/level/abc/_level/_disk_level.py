from __future__ import annotations

from abc import abstractmethod

from ._level import Level, LevelPrivateT


class DiskLevel(Level[LevelPrivateT]):
    """A level base class for all levels with data on disk."""

    __slots__ = ()

    @property
    @abstractmethod
    def path(self) -> str:
        """The path to the level on disk."""
        raise NotImplementedError
