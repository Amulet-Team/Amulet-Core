from abc import abstractmethod
import os
import warnings
from typing import Any, Optional, TYPE_CHECKING

from amulet import IMG_DIRECTORY
from .format_wrapper import FormatWrapper

if TYPE_CHECKING:
    from amulet.api.wrapper import Interface

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
    @abstractmethod
    def world_name(self, value: str):
        raise NotImplementedError

    @property
    @abstractmethod
    def last_played(self) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
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

    @property
    def can_add_dimension(self) -> bool:
        """Can external code register a new dimension.
        If False register_dimension will have no effect."""
        return True

    def _get_interface(self, raw_chunk_data: Optional[Any] = None) -> "Interface":
        from amulet.level.loader import Interfaces

        key = self._get_interface_key(raw_chunk_data)
        return Interfaces.get(key)

    @abstractmethod
    def _get_interface_key(self, raw_chunk_data: Optional[Any] = None) -> Any:
        raise NotImplementedError
