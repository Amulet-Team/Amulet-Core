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
        decoder_id = decoder_loader.identify(decoder_key)
        decoder = decoder_loader.get_decoder(decoder_id)

        chunk, chunk_palette = decoder.decode(decoder_data)
        translator_key = decoder.get_translator(decoder_data)
        translator_id = translator_loader.identify(translator_key)

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

    def save_chunk(self, chunk: Chunk, palette: BlockManager, decoder_id: str, translator_id: str):
        """
        Saves a universal amulet.api.chunk.Chunk object using the given decoder and translator.

        TODO: This changes the chunk and palette to only include blocks used in the chunk, translates them with the translator,
        and then calls the decoder passing in the translator. It then calls _put_encoded to store the data returned by the decoder

        The passed ids will be send to decoder_loader.get_decoder, *not* .identify.
        """

    def _put_decoder(self, cx: int, cz: int, data: Any):
        """
        Actually stores the data from the decoder to disk.
        """

    def _get_decoder(self, cx: int, cz: int) -> Tuple[Tuple, Any]:
        """
        Return the decoder key and data to decode given chunk coordinates.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :return: The decoder key for the identify method and the data to decode.
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
