from __future__ import annotations

from abc import abstractmethod

from ._level import BaseLevel, metadata


class DiskLevel(BaseLevel):
    """A level base class for all levels with data on disk."""

    __slots__ = ()

    @metadata
    @property
    @abstractmethod
    def path(self) -> str:
        """The path to the level on disk."""
        raise NotImplementedError
