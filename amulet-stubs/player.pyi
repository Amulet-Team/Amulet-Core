from _typeshed import Incomplete
from amulet.api.data_types import Dimension as Dimension
from typing import Tuple

LOCAL_PLAYER: str

class Player:
    _player_id: Incomplete
    _location: Incomplete
    _rotation: Incomplete
    _dimension: Incomplete
    def __init__(self, player_id: str, dimension: str, location: Tuple[float, float, float], rotation: Tuple[float, float]) -> None:
        """
        Creates a new instance of :class:`Player` with the given UUID, location, and rotation

        :param player_id: The ID of the player
        :param location: The location of the player in world coordinates
        :param rotation: The rotation of the player
        :param dimension: The dimension the player is in
        """
    def __repr__(self) -> str: ...
    @property
    def player_id(self) -> str:
        """The player's ID"""
    @property
    def location(self) -> Tuple[float, float, float]:
        """The current location of the player in the world"""
    @property
    def rotation(self) -> Tuple[float, float]:
        """The current rotation of the player in the world"""
    @property
    def dimension(self) -> Dimension:
        """The current dimension the player is in"""
