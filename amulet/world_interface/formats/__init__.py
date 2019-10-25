from __future__ import annotations

import os
from typing import Tuple, Any

import numpy
import PyMCTranslate

from amulet.world_interface.chunk import interfaces
from ...api.block import BlockManager
from ...api.chunk import Chunk
from ..loader import Loader

SUPPORTED_FORMAT_VERSION = 0
SUPPORTED_META_VERSION = 0

FORMATS_DIRECTORY = os.path.dirname(__file__)

loader = Loader('format', FORMATS_DIRECTORY, SUPPORTED_META_VERSION, SUPPORTED_FORMAT_VERSION, create_instance=False)


class Format:
    def __init__(self, directory: str):
        self._directory = directory
        self.translation_manager = PyMCTranslate.new_translation_manager()
        self._max_world_version_ = None

    @staticmethod
    def is_valid(directory: str) -> bool:
        """
        Returns whether this format is able to load a given world.

        :param directory: The path to the root of the world to load.
        :return: True if the world can be loaded by this format, False otherwise.
        """
        raise NotImplementedError()

    def max_world_version(self) -> Tuple:
        if self._max_world_version_ is None:
            self._max_world_version_ = self._max_world_version()
        return self._max_world_version()

    def _max_world_version(self) -> Tuple:
        raise NotImplementedError

    def _get_interface(self, max_world_version, raw_chunk_data=None) -> interfaces.Interface:
        if raw_chunk_data:
            key = self._get_interface_key(raw_chunk_data)
        else:
            key = max_world_version
        return interfaces.loader.get(key)

    def _get_interface_key(self, raw_chunk_data) -> Any:
        raise NotImplementedError

    def save(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def all_chunk_keys(self):
        raise NotImplementedError

    def load_chunk(
        self, cx: int, cz: int, global_palette: BlockManager
    ) -> Chunk:
        return self._load_chunk(cx, cz, global_palette)

    def _load_chunk(
        self, cx: int, cz: int, global_palette: BlockManager, recurse: bool = True
    ) -> Chunk:
        """
        Loads and creates a universal amulet.api.chunk.Chunk object from chunk coordinates.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :return: The chunk at the given coordinates.
        """

        # Gets an interface (the code that actually reads the chunk data)
        raw_chunk_data = self._get_raw_chunk_data(cx, cz)
        interface = self._get_interface(self.max_world_version(), raw_chunk_data)
        # get the translator for the given version
        translator, chunk_version = interface.get_translator(self.max_world_version(), raw_chunk_data)

        # decode the raw chunk data into the universal format
        chunk, chunk_palette = interface.decode(raw_chunk_data)

        # set up a callback that translator can use to get chunk data
        if recurse:
            def callback(x, z):
                palette = BlockManager()
                chunk_ = self._load_chunk(cx + x, cz + z, palette, False)
                return chunk_, palette

        else:
            callback = None

        # translate the data to universal format
        chunk, chunk_palette = translator.to_universal(chunk_version, self.translation_manager, chunk, chunk_palette, callback, recurse)

        # convert the block numerical ids from local chunk palette to global palette
        chunk_to_global = numpy.array([global_palette.get_add_block(block) for block in chunk_palette])
        chunk._blocks = chunk_to_global[chunk.blocks]
        return chunk

    def save_chunk(self, chunk: Chunk, global_palette: BlockManager, recurse: bool = True):
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
        chunk._blocks = blocks_.reshape(blocks_shape)
        chunk_palette = numpy.array([global_palette[int_id] for int_id in chunk_palette])

        callback = None  # TODO will need access to the world class

        # translate from universal format to version format
        chunk, chunk_palette = translator.from_universal(chunk_version, self.translation_manager, chunk, chunk_palette, callback, recurse)

        raw_chunk_data = interface.encode(chunk, chunk_palette)

        self._put_raw_chunk_data(cx, cz, raw_chunk_data)

    def delete_chunk(self, cx: int, cz: int):
        raise NotImplementedError

    def _put_raw_chunk_data(self, cx: int, cz: int, data: Any):
        """
        Actually stores the data from the interface to disk.
        """
        raise NotImplementedError()

    def _get_raw_chunk_data(self, cx: int, cz: int) -> Any:
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
