from __future__ import annotations

from typing import Tuple, Optional, Iterator


class PlayerManager:
    def list_players(self) -> Iterator[str]:
        raise NotImplementedError

    def get_player(self, identifier) -> Optional[Player]:
        raise NotImplementedError

    @property
    def local_player(self) -> Optional[Player]:
        raise NotImplementedError


class Player:
    def __init__(self, uuid, nbt):
        self._uuid = uuid
        self._nbt = nbt

    @property
    def uuid(self) -> str:
        return self._uuid

    @property
    def position(self) -> Tuple[float, float, float]:
        raise NotImplementedError

    @property
    def rotation(self) -> Tuple[float, float]:
        raise NotImplementedError
