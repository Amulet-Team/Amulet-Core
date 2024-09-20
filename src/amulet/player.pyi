from amulet.data_types import DimensionId as DimensionId

LOCAL_PLAYER: str

class Player:
    def __init__(
        self,
        player_id: str,
        dimension_id: DimensionId,
        location: tuple[float, float, float],
        rotation: tuple[float, float],
    ) -> None:
        """
        Creates a new instance of :class:`Player` with the given UUID, location, and rotation

        :param player_id: The ID of the player
        :param location: The location of the player in world coordinates
        :param rotation: The rotation of the player
        :param dimension_id: The dimension the player is in
        """

    @property
    def player_id(self) -> str:
        """The player's ID"""

    @property
    def location(self) -> tuple[float, float, float]:
        """The current location of the player in the world"""

    @property
    def rotation(self) -> tuple[float, float]:
        """The current rotation of the player in the world"""

    @property
    def dimension_id(self) -> DimensionId:
        """The current dimension the player is in"""
