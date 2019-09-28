from __future__ import annotations

from typing import Tuple, Any

from ...api.block import BlockManager
from ...api.chunk import Chunk
from .. import decoder_loader
from .. import translator_loader


class Format:
    def __init__(self, directory: str):
        self._directory = directory

    def load_chunk(
        self, cx: int, cz: int, palette: BlockManager, recurse: bool = True
    ) -> Chunk:
        """
        Loads and creates a universal amulet.api.chunk.Chunk object from chunk coordinates.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :return: The chunk at the given coordinates.
        """
        decoder_key, decoder_data = self._get_decoder(cx, cz)
        translator_key = self._get_translator(cx, cz)
        decoder_id = decoder_loader.identify(decoder_key)
        translator_id = translator_loader.identify(translator_key)

        chunk, chunk_palette = decoder_loader.get_decoder(decoder_id).decode(
            decoder_data
        )
        if recurse:

            def callback(x, z):
                palette = BlockManager()
                chunk = self.load_chunk(cx + x, cz + z, palette, False)
                return chunk, palette

        else:
            callback = None
        chunk, chunk_palette = translator_loader.get_translator(
            translator_id
        ).to_universal(chunk, chunk_palette, callback)

        for block, index in chunk_palette._block_to_index_map.items():
            chunk._blocks[chunk._blocks == index] = palette.get_add_block(block)
        return chunk

    def _get_decoder(self, cx: int, cz: int) -> Tuple[Tuple, Any]:
        """
        Return the decoder key and data to decode given chunk coordinates.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :return: The decoder key for the identify method and the data to decode.
        """
        raise NotImplementedError()

    def _get_translator(self, cx: int, cz: int) -> Tuple:
        """
        Return the translator key given chunk coordinates.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :return: The translator key for the identify method.
        """
        raise NotImplementedError()

    @staticmethod
    def identify(directory: str) -> bool:
        """
        Returns whether this format is able to load a given world.

        :param directory: The path to the root of the world to load.
        :return: True if the world can be loaded by this format, False otherwise.
        """
        raise NotImplementedError()
