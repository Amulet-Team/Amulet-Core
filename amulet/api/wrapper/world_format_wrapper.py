import os
import warnings
from typing import Any, Generator, List, Tuple, Dict, TYPE_CHECKING

from amulet import IMG_DIRECTORY, ChunkCoordinates
from amulet.api.data_types import Dimension, PlatformType
from .format_wrapper import FormatWrapper
from amulet.world_interface.chunk import interfaces

missing_world_icon = os.path.abspath(
    os.path.join(IMG_DIRECTORY, "missing_world_icon.png")
)

if TYPE_CHECKING:
    from amulet.api.wrapper import Interface


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

    @staticmethod
    def is_valid(path: str) -> bool:
        raise NotImplementedError

    @property
    def valid_formats(self) -> Dict[PlatformType, Tuple[bool, bool]]:
        raise NotImplementedError

    @property
    def can_add_dimension(self) -> bool:
        """Can external code register a new dimension.
        If False register_dimension will have no effect."""
        return True

    @property
    def dimensions(self) -> List[Dimension]:
        raise NotImplementedError

    def register_dimension(self, dimension_internal: Any, dimension_name: Dimension):
        raise NotImplementedError

    def _get_interface(self, max_world_version, raw_chunk_data=None) -> "Interface":
        if raw_chunk_data:
            key = self._get_interface_key(raw_chunk_data)
        else:
            key = max_world_version
        return interfaces.loader.get(key)

    def _get_interface_key(self, raw_chunk_data) -> Any:
        raise NotImplementedError

    def _create_and_open(self):
        raise NotImplementedError

    def _open(self):
        raise NotImplementedError

    def _save(self):
        raise NotImplementedError

    def _close(self):
        raise NotImplementedError

    def unload(self):
        raise NotImplementedError

    def all_chunk_coords(
        self, dimension: Dimension
    ) -> Generator[ChunkCoordinates, None, None]:
        raise NotImplementedError

    def _delete_chunk(self, cx: int, cz: int, dimension: Dimension):
        raise NotImplementedError

    def _put_raw_chunk_data(self, cx: int, cz: int, data: Any, dimension: Dimension):
        raise NotImplementedError

    def _get_raw_chunk_data(self, cx: int, cz: int, dimension: Dimension) -> Any:
        raise NotImplementedError
