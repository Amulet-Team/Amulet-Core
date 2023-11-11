from .base_level import BaseLevel as BaseLevel
from amulet.api.wrapper import WorldFormatWrapper as WorldFormatWrapper

class World(BaseLevel):
    """
    Class that handles world editing of any world format via an separate and flexible data format
    """
    def __init__(self, directory: str, world_wrapper: WorldFormatWrapper) -> None: ...
    @property
    def level_wrapper(self) -> WorldFormatWrapper:
        """A class to access data directly from the level."""
