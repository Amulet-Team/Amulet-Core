from abc import abstractmethod
import os
from typing import Any, Optional, TYPE_CHECKING

from amulet import IMG_DIRECTORY
from .format_wrapper import FormatWrapper, VersionNumberT

if TYPE_CHECKING:
    from amulet.api.wrapper import Interface

missing_world_icon = os.path.abspath(
    os.path.join(IMG_DIRECTORY, "missing_world_icon.png")
)


class WorldFormatWrapper(FormatWrapper[VersionNumberT]):
    _missing_world_icon = missing_world_icon

    def __init__(self, path: str):
        """
        Construct a new instance of :class:`WorldFormatWrapper`.

        This should not be used directly. You should instead use :func:`amulet.load_format`.

        :param path: The file path to the serialised data.
        """
        super().__init__(path)
        self._world_image_path = missing_world_icon

    @property
    @abstractmethod
    def level_name(self) -> str:
        raise NotImplementedError

    @level_name.setter
    @abstractmethod
    def level_name(self, value: str):
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
    def world_image_path(self) -> str:
        """The path to the world icon."""
        return self._world_image_path

    @property
    def can_add_dimension(self) -> bool:
        return False

    def register_dimension(self, dimension_identifier: Any):
        pass

    def _get_interface(self, raw_chunk_data: Optional[Any] = None) -> "Interface":
        raise NotImplementedError
