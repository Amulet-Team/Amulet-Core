from __future__ import annotations

from ._level import BaseLevelPrivate


class LevelFriend:
    _l: BaseLevelPrivate

    __slots__ = ("_l",)

    def __init__(self, level_data: BaseLevelPrivate):
        self._l = level_data
