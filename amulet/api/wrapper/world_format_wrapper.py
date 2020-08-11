from typing import Tuple, Any, Union, Generator, List, Optional, TYPE_CHECKING
import traceback
import os

from amulet import log, IMG_DIRECTORY
from amulet.api.data_types import ChunkCoordinates
from .format_wrapper import BaseFormatWrapper

if TYPE_CHECKING:
    from amulet.api.chunk import Chunk
    from amulet.api.data_types import Dimension

missing_world_icon = os.path.abspath(
    os.path.join(IMG_DIRECTORY, "missing_world_icon.png")
)


class WorldFormatWrapper(BaseFormatWrapper):
    _missing_world_icon = missing_world_icon

    def __init__(self, world_path: str):
        super().__init__()
        self._path = world_path
        self._world_image_path = missing_world_icon
        self._changed: bool = False

    @property
    def sub_chunk_size(self) -> int:
        return 16

    @property
    def chunk_size(self) -> Tuple[int, Union[int, None], int]:
        return self.sub_chunk_size, self.sub_chunk_size * 16, self.sub_chunk_size

    @property
    def path(self) -> str:
        """The path to the world directory"""
        return self._path

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
        log.info(
            f"Format.world_path is depreciated. Please used Format.path{traceback.format_exc()}"
        )
        return self._path

    @property
    def world_image_path(self) -> str:
        """The path to the world icon"""
        return self._world_image_path

    @property
    def dimensions(self) -> List["Dimension"]:
        """A list of all the dimensions contained in the world"""
        raise NotImplementedError

    def register_dimension(
        self, dimension_internal: Any, dimension_name: Optional["Dimension"] = None
    ):
        """
        Register a new dimension.
        :param dimension_internal: The internal representation of the dimension
        :param dimension_name: The name of the dimension shown to the user
        :return:
        """
        raise NotImplementedError

    def all_chunk_coords(
        self, dimension: "Dimension"
    ) -> Generator[ChunkCoordinates, None, None]:
        """A generator of all chunk coords in the given dimension"""
        raise NotImplementedError

    def load_chunk(self, cx: int, cz: int, dimension: "Dimension") -> "Chunk":
        """
        Loads and creates a universal amulet.api.chunk.Chunk object from chunk coordinates.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param dimension: dimension
        :return: The chunk at the given coordinates.
        """
        return super().load_chunk(cx, cz, dimension)

    def commit_chunk(self, chunk: "Chunk", dimension: "Dimension"):
        """
        Save a universal format chunk to the Format database (not the disk database)
        call save method to write changed chunks back to the disk database
        :param chunk: The chunk object to translate and save
        :param dimension: optional dimension
        :return:
        """
        super().commit_chunk(chunk, dimension)

    def delete_chunk(self, cx: int, cz: int, dimension: "Dimension"):
        raise NotImplementedError

    def _put_raw_chunk_data(
        self, cx: int, cz: int, data: Any, dimension: "Dimension", *args
    ):
        """
        Actually stores the data from the interface to disk.
        """
        raise NotImplementedError()

    def _get_raw_chunk_data(
        self, cx: int, cz: int, dimension: "Dimension", *args
    ) -> Any:
        """
        Return the interface key and data to interface with given chunk coordinates.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :return: The interface key for the get_interface method and the data to interface with.
        """
        raise NotImplementedError()
