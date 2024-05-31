from __future__ import annotations

from .base_level import BaseLevel
from amulet.api.wrapper import WorldFormatWrapper


class World(BaseLevel):
    """
    Class that handles world editing of any world format via an separate and flexible data format
    """

    def __init__(self, directory: str, world_wrapper: WorldFormatWrapper):
        assert isinstance(world_wrapper, WorldFormatWrapper)
        super().__init__(directory, world_wrapper)

    @property
    def level_wrapper(self) -> "WorldFormatWrapper":
        """A class to access data directly from the level."""
        return self._level_wrapper
