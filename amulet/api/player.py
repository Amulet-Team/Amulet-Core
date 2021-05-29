from __future__ import annotations

from typing import Tuple

from amulet.api.history import Changeable
from amulet.api.data_types import Dimension

LOCAL_PLAYER = "~local_player"


class Player(Changeable):
    def __init__(
        self,
        player_id: str,
        dimension: str,
        location: Tuple[float, float, float],
        rotation: Tuple[float, float],
    ):
        """
        Creates a new instance of :class:`Player` with the given UUID, location, and rotation

        :param player_id: The ID of the player
        :param location: The location of the player in world coordinates
        :param rotation: The rotation of the player
        :param dimension: The dimension the player is in
        """
        super().__init__()
        assert isinstance(player_id, str)
        assert (
            isinstance(location, tuple)
            and len(location) == 3
            and all(isinstance(f, float) for f in location)
        )
        assert (
            isinstance(rotation, tuple)
            and len(rotation) == 2
            and all(isinstance(f, float) for f in rotation)
        )
        self._player_id = player_id
        self._location = location
        self._rotation = rotation
        self._dimension = dimension

    def __repr__(self):
        return f"Player({self.player_id}, {self.dimension}, {self.location}, {self.rotation})"

    @property
    def player_id(self) -> str:
        """The player's ID"""
        return self._player_id

    @property
    def location(self) -> Tuple[float, float, float]:
        """The current location of the player in the world"""
        return self._location

    @property
    def rotation(self) -> Tuple[float, float]:
        """The current rotation of the player in the world"""
        return self._rotation

    @property
    def dimension(self) -> Dimension:
        """The current dimension the player is in"""
        return self._dimension
