from __future__ import annotations

from amulet.level.base_level import BaseLevel, CreatableLevel


class TemporaryLevel(BaseLevel, CreatableLevel):
    """A temporary level that exists only in memory."""

    __slots__ = ()

    @classmethod
    def create(cls, *args, **kwargs) -> TemporaryLevel:
        raise NotImplementedError
