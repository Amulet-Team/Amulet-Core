from __future__ import annotations

from typing import TypeVar, Generic
from weakref import ref
from runtime_final import final

from ._level import BaseLevel, BaseLevelPrivate

LevelT = TypeVar("LevelT", bound=BaseLevel)
LevelDataT = TypeVar("LevelDataT", bound=BaseLevelPrivate)


class LevelFriend(Generic[LevelT, LevelDataT]):
    _d: LevelDataT

    __slots__ = (
        "_level_ref",
        "_d",
    )

    def __init__(self, level: LevelT, data: LevelDataT):
        self._level_ref = ref(level)
        self._d = data

    @final
    @property
    def _level(self) -> LevelT:
        level = self._level_ref()
        if level is None:
            raise RuntimeError("The level no longer exists.")
        return level
