import os
import warnings

from amulet import log, IMG_DIRECTORY
from .format_wrapper import FormatWrapper

missing_world_icon = os.path.abspath(
    os.path.join(IMG_DIRECTORY, "missing_world_icon.png")
)


class WorldFormatWrapper(FormatWrapper):
    _missing_world_icon = missing_world_icon

    def __init__(self, world_path: str):
        super().__init__(world_path)
        self._world_image_path = missing_world_icon
        self._changed: bool = False

    @property
    def world_name(self) -> str:
        """The name of the world"""
        return "Unknown World"

    @world_name.setter
    def world_name(self, value: str):
        raise NotImplementedError

    @property
    def last_played(self) -> int:
        raise NotImplementedError

    @property
    def game_version_string(self) -> str:
        raise NotImplementedError

    @property
    def world_path(self) -> str:
        """The path to the world directory"""
        warnings.warn(
            "Format.world_path is depreciated and will be removed in the future. Please used WorldFormatWrapper.path instead",
            DeprecationWarning,
        )
        return self._path

    @property
    def world_image_path(self) -> str:
        """The path to the world icon"""
        return self._world_image_path
