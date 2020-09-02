from __future__ import annotations

from os.path import join as opjoin, basename, exists
from glob import iglob
from typing import Tuple, Optional, Iterator

from amulet.api.player_data.common import Player, PlayerManager

import amulet_nbt as nbt


class JavaPlayerManager(PlayerManager):
    def __init__(self, format_wrapper):
        self._world_path = format_wrapper.path

    def list_players(self) -> Iterator[str]:
        yield from (
            uuid[0 : uuid.rfind(".")]
            for uuid in (
                basename(f)
                for f in iglob(opjoin(self._world_path, "playerdata", "*.dat"))
            )
        )

    def get_player(self, identifier) -> Optional[JavaPlayer]:
        dat_path = opjoin(self._world_path, "playerdata", f"{identifier}.dat")
        if exists(dat_path):
            player_nbt = nbt.load(dat_path)
            return JavaPlayer(identifier, player_nbt)
        return None

    @property
    def local_player(self) -> Optional[JavaPlayer]:
        level_nbt = nbt.load(opjoin(self._world_path, "level.dat"))
        if "Player" in level_nbt:
            return JavaPlayer("~local_player", level_nbt)
        return None


class JavaPlayer(Player):
    @property
    def position(self) -> Tuple[float, float, float]:
        return tuple(map(float, self._nbt["Pos"].value))[0:3]

    @property
    def rotation(self) -> Tuple[float, float]:
        return tuple(map(float, self._nbt["Rotation"].value))[0:2]
