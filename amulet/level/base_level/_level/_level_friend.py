from __future__ import annotations

from typing import TypeVar, Generic
from weakref import ref
from runtime_final import final

from ._level import BaseLevel, BaseLevelPrivate

LevelT = TypeVar("LevelT", bound=BaseLevel)
LevelDataT = TypeVar("LevelDataT", bound=BaseLevelPrivate)


class LevelFriend(Generic[LevelT, LevelDataT]):
    __slots__ = (
        "_level_ref",
        "_d",
    )

    @final
    def __init__(self, level: LevelT, data: LevelDataT):
        self._level_ref = ref(level)
        self._d = data
        self._init()

    def _init(self):
        """Initialise instance attributes"""
        pass

    @final
    @property
    def _level(self) -> LevelT:
        level = self._level_ref()
        if level is None:
            raise RuntimeError("The level no longer exists.")
        return level
