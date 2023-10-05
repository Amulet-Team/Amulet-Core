from __future__ import annotations

from typing import TypeVar, Generic
from weakref import ref
from runtime_final import final

from .._base_level import BaseLevel, BaseLevelPrivate

LevelT = TypeVar("LevelT", bound=BaseLevel)
LevelDataT = TypeVar("LevelDataT", bound=BaseLevelPrivate)


class LevelNamespace(Generic[LevelT]):
    __slots__ = (
        "_level_ref",
        "_data",
    )

    @final
    def __init__(self, level: LevelT, data: LevelDataT):
        self._level_ref = ref(level)
        self._data = data
        self._init()

    def _init(self):
        """Initialise instance attributes"""
        pass

    @final
    def _get_level(self) -> LevelT:
        level = self._level_ref()
        if level is None:
            raise RuntimeError("The level no longer exists.")
        return level
