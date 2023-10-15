from __future__ import annotations

from ._level import BaseLevelPrivate


class LevelFriend:
    _d: BaseLevelPrivate

    __slots__ = ("_d",)

    def __init__(self, level_data: BaseLevelPrivate):
        self._d = level_data
