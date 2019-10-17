from __future__ import annotations

from typing import Tuple, Any

from ...api.block import BlockManager
from ...api.chunk import Chunk
from .. import interface_loader
from .. import translator_loader
import PyMCTranslate


class Format:
    def __init__(self, directory: str):
        self._directory = directory
        self.translation_manager = PyMCTranslate.new_translation_manager()

    def load_chunk(
        self, cx: int, cz: int, palette: BlockManager
    ) -> Chunk:
        return self._load_chunk(cx, cz, palette)

    def _load_chunk(
        self, cx: int, cz: int, palette: BlockManager, recurse: bool = True
    ) -> Chunk:
        """
        Loads and creates a universal amulet.api.chunk.Chunk object from chunk coordinates.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :return: The chunk at the given coordinates.
        """

        # Gets an interface (the code that actually reads the chunk data)
        interface_key, interface_data = self._load_chunk_data(cx, cz)
        interface = interface_loader.get_interface(interface_key)

        # decode the raw chunk data into the universal format
        chunk, chunk_palette = interface.decode(interface_data)

        # set up a callback that translator can use to get chunk data
        # TODO: perhaps find a way so that this does not need to load the whole chunk
        if recurse:
            def callback(x, z):
                palette = BlockManager()
                chunk = self._load_chunk(cx + x, cz + z, palette, False)  # TODO: this will also translate the chunk
                return chunk, palette

        else:
            callback = None

        # get the translator for the given version and translate the data to universal format
        translator_key = interface.get_translator(interface_data)
        translator = translator_loader.get_translator(translator_key)
        chunk, chunk_palette = translator.to_universal(self.translation_manager, chunk, chunk_palette, callback, recurse)

        for block, index in chunk_palette._block_to_index_map.items():
            chunk._blocks[chunk._blocks == index] = palette.get_add_block(block)
        return chunk

    def save_chunk(self, chunk: Chunk, palette: BlockManager, interface_id: str, translator_id: str):
        """
        Saves a universal amulet.api.chunk.Chunk object using the given interface and translator.

        TODO: This changes the chunk and palette to only include blocks used in the chunk, translates them with the translator,
        and then calls the interface passing in the translator. It then calls _put_encoded to store the data returned by the interface

        The passed ids will be send to interface_loader.get_interface, *not* .identify.
        """
        raise NotImplementedError()

    def _save_chunk_data(self, cx: int, cz: int, data: Any):
        """
        Actually stores the data from the interface to disk.
        """
        raise NotImplementedError()

    def _load_chunk_data(self, cx: int, cz: int) -> Tuple[Tuple, Any]:
        """
        Return the interface key and data to interface with given chunk coordinates.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :return: The interface key for the get_interface method and the data to interface with.
        """
        raise NotImplementedError()

    @staticmethod
    def is_valid(directory: str) -> bool:
        """
        Returns whether this format is able to load a given world.

        :param directory: The path to the root of the world to load.
        :return: True if the world can be loaded by this format, False otherwise.
        """
        raise NotImplementedError()
