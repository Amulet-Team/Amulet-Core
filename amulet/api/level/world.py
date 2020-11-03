from __future__ import annotations
import warnings

from .base_level import BaseLevel
from amulet.api.wrapper import WorldFormatWrapper


class World(BaseLevel):
    """
    Class that handles world editing of any world format via an separate and flexible data format
    """

    def __init__(
        self, directory: str, world_wrapper: WorldFormatWrapper, temp_dir: str = None
    ):
        assert isinstance(world_wrapper, WorldFormatWrapper)
        super().__init__(directory, world_wrapper, temp_dir)

    @property
    def world_wrapper(self) -> WorldFormatWrapper:
        warnings.warn(
            "BaseLevel.world_wrapper is depreciated and will be removed in the future. Please use BaseLevel.level_wrapper instead.",
            DeprecationWarning,
        )
        return self._level_wrapper
