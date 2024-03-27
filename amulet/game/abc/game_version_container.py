from __future__ import annotations

from typing import TYPE_CHECKING
from weakref import ref

if TYPE_CHECKING:
    from .version import GameVersion


class GameVersionContainer:
    def __init__(self, game_version: GameVersion):
        self.__game_version_ref = ref(game_version)

    @property
    def _game_version(self) -> GameVersion:
        game = self.__game_version_ref()
        if game is None:
            raise ReferenceError("Referenced GameVersion no longer exists.")
        return game

    def __getstate__(self) -> dict:
        return {"_game_version": self._game_version}

    def __setstate__(self, state: dict) -> None:
        self.__game_version_ref = ref(state["_game_version"])
