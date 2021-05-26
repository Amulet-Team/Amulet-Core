from __future__ import annotations

from typing import Tuple

from amulet.api.history import Changeable

LOCAL_PLAYER = "~local_player"


class Player(Changeable):
    def __init__(
        self,
        player_id: str,
        position: Tuple[float, float, float],
        rotation: Tuple[float, float],
        dimension: str,
    ):
        """
        Creates a new instance of :class:`Player` with the given UUID, position, and rotation

        :param player_id: The ID of the player
        :param position: The position of the player in world coordinates
        :param rotation: The rotation of the player
        :param dimension: The dimension the player is in
        """
        super().__init__()
        assert isinstance(player_id, str)
        assert (
            isinstance(position, tuple)
            and len(position) == 3
            and all(isinstance(f, float) for f in position)
        )
        assert (
            isinstance(rotation, tuple)
            and len(rotation) == 2
            and all(isinstance(f, float) for f in rotation)
        )
        self._player_id = player_id
        self._position = position
        self._rotation = rotation
        self._dimension = dimension

    @property
    def player_id(self) -> str:
        """The player's ID"""
        return self._player_id

    @property
    def position(self) -> Tuple[float, float, float]:
        """The current position of the player in the world"""
        return self._position

    @property
    def rotation(self) -> Tuple[float, float]:
        """The current rotation of the player in the world"""
        return self._rotation

    @property
    def dimension(self) -> str:
        """The current dimension the player is in"""
        return self._dimension
