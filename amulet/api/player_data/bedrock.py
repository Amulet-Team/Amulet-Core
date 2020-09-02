from __future__ import annotations

from typing import Tuple, Optional, Iterator

from amulet.api.player_data.common import Player, PlayerManager

import amulet_nbt as nbt


class BedrockPlayerManager(PlayerManager):
    def __init__(self, format_wrapper):
        self._db = format_wrapper._level_manager._db

    def list_players(self) -> Iterator[str]:
        return (
            player_id[14:].decode("utf-8")
            for player_id in self._db.keys()
            if "player" in str(player_id) and player_id != b"~local_player"
        )

    def get_player(self, identifier) -> Optional[Player]:
        key = f"player_server_{identifier}".encode("utf-8")
        data = self._db.get(key)
        return BedrockPlayer(
            identifier, nbt.load(buffer=data, compressed=False, little_endian=True)
        )

    @property
    def local_player(self) -> Optional[Player]:
        if b"~local_player" in self._db.keys():
            return BedrockPlayer(
                "~local_player",
                nbt.load(
                    buffer=self._db.get(b"~local_player"),
                    compressed=False,
                    little_endian=True,
                ),
            )
        return None


class BedrockPlayer(Player):
    @property
    def position(self) -> Tuple[float, float, float]:
        return tuple(map(float, self._nbt["Pos"].value))[0:3]

    @property
    def rotation(self) -> Tuple[float, float]:
        return tuple(map(float, self._nbt["Rotation"].value))[0:2]
