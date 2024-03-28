from __future__ import annotations

from amulet.level.abc import Level, CreatableLevel


class TemporaryLevel(Level, CreatableLevel):
    """A temporary level that exists only in memory."""

    __slots__ = ()

    @classmethod
    def create(cls) -> TemporaryLevel:
        return cls()
