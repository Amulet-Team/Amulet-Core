from __future__ import annotations

import os
from typing import Tuple, Any, Union, Generator, Dict

import numpy
import PyMCTranslate

from amulet import log
from amulet.world_interface.chunk import interfaces
from amulet.api.errors import (
    ChunkLoadError,
    ChunkDoesNotExist,
    WorldDatabaseAccessException,
)
from ...api.block import BlockManager
from ...api.chunk import Chunk
from ..loader import Loader

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


class Format:
    _missing_world_icon = missing_world_icon

    def __init__(self, world_path: str):
        self._world_path = world_path
        self._translation_manager = None
        self._max_world_version_ = None
        self._world_image_path = missing_world_icon
        self._changed: bool = False

    @property
    def translation_manager(self) -> PyMCTranslate.TranslationManager:
        """The translation manager attached to the world"""
        if self._translation_manager is None:
            self._translation_manager = PyMCTranslate.new_translation_manager()
        return self._translation_manager

    @translation_manager.setter
    def translation_manager(self, value: PyMCTranslate.TranslationManager):
        self._translation_manager = value

    @staticmethod
    def is_valid(directory: str) -> bool:
        """
        Returns whether this format is able to load a given world.

        :param directory: The path to the root of the world to load.
        :return: True if the world can be loaded by this format, False otherwise.
        """
        raise NotImplementedError()

    @property
    def platform(self) -> str:
        """Platform string ("bedrock" / "java" / ...)"""
        raise NotImplementedError

    def max_world_version(self) -> Tuple[str, Union[int, Tuple[int, int, int]]]:
        """The version the world was last opened in
        This should be greater than or equal to the chunk versions found within"""
        if self._max_world_version_ is None:
            self._max_world_version_ = self._max_world_version()
        return self._max_world_version()

    def _max_world_version(self) -> Tuple[str, Union[int, Tuple[int, int, int]]]:
        raise NotImplementedError

    @property
    def chunk_size(self) -> Tuple[int, int, int]:
        return (16, 256, 16)

    @property
    def changed(self) -> bool:
        return self._changed

    @property
    def world_name(self) -> str:
        """The name of the world"""
        return "Unknown World"

    @world_name.setter
    def world_name(self, value: str):
        raise NotImplementedError

    @property
    def game_version_string(self) -> str:
        raise NotImplementedError

    @property
    def world_path(self) -> str:
        """The path to the world directory"""
        return self._world_path

    @property
    def world_image_path(self) -> str:
        """The path to the world icon"""
        return self._world_image_path

    @property
    def dimensions(self) -> Dict[str, int]:
        """A list of all the dimensions contained in the world"""
        raise NotImplementedError

    def _get_interface(
        self, max_world_version, raw_chunk_data=None
    ) -> interfaces.Interface:
        if raw_chunk_data:
            key = self._get_interface_key(raw_chunk_data)
        else:
            key = max_world_version
        return interfaces.loader.get(key)

    def _get_interface_key(self, raw_chunk_data) -> Any:
        raise NotImplementedError

    def open(self):
        """Open the database for reading and writing"""
        raise NotImplementedError

    def has_lock(self) -> bool:
        """Verify that the world database can be read and written"""
        raise NotImplementedError

    def _verify_has_lock(self):
        """Ensure that the Format has a lock on the world. Throw WorldAccessException if not"""
        if not self.has_lock():
            raise WorldDatabaseAccessException(
                "The world has been opened somewhere else or the .open() method was not called"
            )

    def save(self):
        """Save the data back to the disk database"""
        raise NotImplementedError

    def close(self):
        """Close the disk database"""
        raise NotImplementedError

    def all_chunk_coords(self, dimension: int = 0) -> Generator[Tuple[int, int]]:
        """A generator of all chunk coords in the given dimension"""
        raise NotImplementedError

    def load_chunk(
        self, cx: int, cz: int, global_palette: BlockManager, dimension: int = 0
    ) -> Chunk:
        """
        Loads and creates a universal amulet.api.chunk.Chunk object from chunk coordinates.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param global_palette: The universal block manager
        :param dimension: optional dimension
        :return: The chunk at the given coordinates.
        """
        try:
            return self._load_chunk(cx, cz, dimension, global_palette)
        except ChunkDoesNotExist as e:
            raise e
        except Exception:
            log.error(f"Error loading chunk {cx} {cz}", exc_info=True)
            raise ChunkLoadError

    def _load_chunk(
        self,
        cx: int,
        cz: int,
        dimension: int,
        global_palette: BlockManager,
        recurse: bool = True,
    ) -> Chunk:
        """
        Loads and creates a universal amulet.api.chunk.Chunk object from chunk coordinates.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param global_palette: The universal block manager
        :param dimension: optional dimension
        :param recurse: bool: look in boundary chunks if required to fully define data
        :return: The chunk at the given coordinates.
        """

        # Gets an interface (the code that actually reads the chunk data)
        raw_chunk_data = self._get_raw_chunk_data(cx, cz)
        interface = self._get_interface(self.max_world_version(), raw_chunk_data)
        # get the translator for the given version
        translator, game_version = interface.get_translator(
            self.max_world_version(), raw_chunk_data
        )

        # decode the raw chunk data into the universal format
        chunk, chunk_palette = interface.decode(cx, cz, raw_chunk_data)

        # set up a callback that translator can use to get chunk data
        if recurse:
            chunk_cache: Dict[Tuple[int, int], Tuple[Chunk, BlockManager]] = {}

            def get_chunk_callback(x: int, z: int) -> Tuple[Chunk, BlockManager]:
                palette = BlockManager()
                cx_, cz_ = cx + x, cz + z
                if (cx_, cz_) not in chunk_cache:
                    chunk_ = self._load_chunk(cx_, cz_, dimension, palette, False)
                    chunk_cache[(cx_, cz_)] = chunk_, palette
                return chunk_cache[(cx_, cz_)]

        else:
            get_chunk_callback = None

        # translate the data to universal format
        chunk, chunk_palette = translator.to_universal(
            game_version,
            self.translation_manager,
            chunk,
            chunk_palette,
            get_chunk_callback,
            recurse,
        )

        # convert the block numerical ids from local chunk palette to global palette
        chunk_to_global = numpy.array(
            [global_palette.get_add_block(block) for block in chunk_palette],
            dtype=numpy.uint,
        )
        chunk.blocks = chunk_to_global[chunk.blocks].reshape(16, 256, 16)
        chunk.changed = False
        return chunk

    def commit_chunk(
        self, chunk: Chunk, global_palette: BlockManager, dimension: int = 0
    ):
        """
        Save a universal format chunk to the Format database (not the disk database)
        call save method to write changed chunks back to the disk database
        :param chunk: The chunk object to translate and save
        :param global_palette: The universal block manager
        :param dimension: optional dimension
        :return:
        """
        try:
            self._commit_chunk(chunk, dimension, global_palette)
        except Exception:
            log.error(f"Error saving chunk {chunk}", exc_info=True)
        self._changed = True

    def _commit_chunk(
        self,
        chunk: Chunk,
        dimension: int,
        global_palette: BlockManager,
        recurse: bool = True,
    ):
        """
        Saves a universal amulet.api.chunk.Chunk object
        Calls the interface then the translator.
        It then calls _put_chunk_data to store the data returned by the interface
        """
        # get the coordinates for later
        cx, cz = chunk.cx, chunk.cz

        # Gets an interface (the code that actually reads the chunk data)
        interface = self._get_interface(self.max_world_version())
        # get the translator for the given version
        translator, chunk_version = interface.get_translator(self.max_world_version())

        # convert the global indexes into local indexes and a local palette
        blocks_shape = chunk.blocks.shape
        chunk_palette, blocks_ = numpy.unique(chunk.blocks, return_inverse=True)
        chunk.blocks = blocks_.reshape(blocks_shape)
        chunk_palette = numpy.array(
            [global_palette[int_id] for int_id in chunk_palette]
        )

        def get_chunk_callback(x: int, z: int) -> Tuple[Chunk, BlockManager]:
            # conversion from universal should not require any data outside the block
            return chunk, global_palette

        # translate from universal format to version format
        chunk, chunk_palette = translator.from_universal(
            chunk_version,
            self.translation_manager,
            chunk,
            chunk_palette,
            get_chunk_callback,
            recurse,
        )

        raw_chunk_data = interface.encode(
            chunk, chunk_palette, self.max_world_version()
        )

        self._put_raw_chunk_data(cx, cz, raw_chunk_data, dimension)

    def delete_chunk(self, cx: int, cz: int, dimension: int = 0):
        raise NotImplementedError

    def _put_raw_chunk_data(self, cx: int, cz: int, data: Any, dimension: int = 0):
        """
        Actually stores the data from the interface to disk.
        """
        raise NotImplementedError()

    def _get_raw_chunk_data(self, cx: int, cz: int, dimension: int = 0) -> Any:
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
