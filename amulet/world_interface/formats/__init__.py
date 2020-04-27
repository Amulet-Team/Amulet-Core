from __future__ import annotations

import os
from typing import Tuple, Any, Union, Generator, List, Optional
import traceback

from amulet import log
from amulet.api.block import BlockManager
from amulet.api.chunk import Chunk
from amulet.api.data_types import Dimension
from amulet.api.wrapper import FormatWraper
from amulet.world_interface.loader import Loader

SUPPORTED_FORMAT_VERSION = 0
SUPPORTED_META_VERSION = 0

FORMATS_DIRECTORY = os.path.dirname(__file__)
missing_world_icon = os.path.abspath(
    os.path.join(FORMATS_DIRECTORY, "..", "..", "img", "missing_world_icon.png")
)

loader = Loader(
    "format",
    FORMATS_DIRECTORY,
    SUPPORTED_META_VERSION,
    SUPPORTED_FORMAT_VERSION,
    create_instance=False,
)


class WorldFormatWrapper(FormatWraper):
    _missing_world_icon = missing_world_icon

    def __init__(self, world_path: str):
        super().__init__(world_path)
        self._world_image_path = missing_world_icon
        self._changed: bool = False

    @property
    def chunk_size(self) -> Tuple[int, Union[int, None], int]:
        return 16, 256, 16

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
    def world_path(self) -> str:
        """The path to the world directory"""
        log.info(f'Format.world_path is depreciated. Please used Format.path{traceback.format_exc()}')
        return self._path

    @property
    def world_image_path(self) -> str:
        """The path to the world icon"""
        return self._world_image_path

    @property
    def dimensions(self) -> List[Dimension]:
        """A list of all the dimensions contained in the world"""
        raise NotImplementedError

    def register_dimension(self, dimension_internal: Any, dimension_name: Optional[Dimension] = None):
        """
        Register a new dimension.
        :param dimension_internal: The internal representation of the dimension
        :param dimension_name: The name of the dimension shown to the user
        :return:
        """
        raise NotImplementedError

    def all_chunk_coords(self, dimension: Dimension) -> Generator[Tuple[int, int]]:
        """A generator of all chunk coords in the given dimension"""
        raise NotImplementedError

    def load_chunk(
        self, cx: int, cz: int, global_palette: BlockManager, dimension: Dimension
    ) -> Chunk:
        """
        Loads and creates a universal amulet.api.chunk.Chunk object from chunk coordinates.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param global_palette: The universal block manager
        :param dimension: dimension
        :return: The chunk at the given coordinates.
        """
        super().load_chunk(cx, cz, global_palette, dimension)

    def delete_chunk(self, cx: int, cz: int, dimension: Dimension):
        raise NotImplementedError

    def _put_raw_chunk_data(self, cx: int, cz: int, data: Any, dimension: Dimension, *args):
        """
        Actually stores the data from the interface to disk.
        """
        raise NotImplementedError()

    def _get_raw_chunk_data(self, cx: int, cz: int, dimension: Dimension, *args) -> Any:
        """
        Return the interface key and data to interface with given chunk coordinates.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :return: The interface key for the get_interface method and the data to interface with.
        """
        raise NotImplementedError()


if __name__ == "__main__":
    import time

    print(loader.get_all())
    time.sleep(1)
    loader.reload()
    print(loader.get_all())
