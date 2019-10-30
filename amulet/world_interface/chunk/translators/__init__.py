from __future__ import annotations

import os
import numpy

from typing import Tuple, Callable, Union

from amulet.api.block import BlockManager
from amulet.api.chunk import Chunk
from amulet.world_interface.loader import Loader
import PyMCTranslate
from PyMCTranslate.py3.translation_manager import Version

SUPPORTED_TRANSLATOR_VERSION = 0
SUPPORTED_META_VERSION = 0

TRANSLATORS_DIRECTORY = os.path.dirname(__file__)

loader = Loader('translator', TRANSLATORS_DIRECTORY, SUPPORTED_META_VERSION, SUPPORTED_TRANSLATOR_VERSION)


class Translator:
    def _translator_key(self, version_number: Union[int, Tuple[int, int, int]]) -> Tuple[str, Union[int, Tuple[int, int, int]]]:
        """
        Return the version key for PyMCTranslate

        :return: The tuple version key for PyMCTranslate
        """
        raise NotImplementedError()

    @staticmethod
    def is_valid(key: Tuple) -> bool:
        """
        Returns whether this translator is able to translate the chunk type with a given identifier key,
        generated by the decoder.

        :param key: The key who's decodability needs to be checked.
        :return: True if this translator is able to translate the chunk type associated with the key, False otherwise.
        """
        raise NotImplementedError()

    def _translate(
            self,
            chunk: Chunk,
            palette: numpy.ndarray,
            callback: Callable,
            translate: Callable,
            full_translate: bool
    ):
        if not full_translate:
            return chunk, palette

        todo = []
        finished = BlockManager()
        palette_mappings = {}

        for i, block in enumerate(palette):
            universal, entity, extra = translate(block)
            if entity:
                print(f"Warning: not sure what to do with entity for {block} yet.")
            if extra and callback:
                todo.append(i)
                continue
            palette_mappings[i] = finished.get_add_block(universal)

        block_mappings = {}
        for index in todo:
            for x, y, z in zip(*numpy.where(chunk.blocks == index)):

                def get_block_at(pos):
                    nonlocal x, y, z, palette, chunk
                    dx, dy, dz = pos
                    dx += x
                    dy += y
                    dz += z
                    cx = dx // 16
                    cz = dz // 16
                    if cx == 0 and cz == 0:
                        return palette[chunk.blocks[dx % 16, dy, dz % 16]], None
                    chunk, palette = callback(cx, cz)
                    block_ = palette[chunk.blocks[dx % 16, dy, dz % 16]]
                    return translate(block_)[0], None

                block = palette[chunk.blocks[x, y, z]]
                universal, entity, extra = translate(block, get_block_at)
                if entity:
                    print(f"Warning: not sure what to do with entity for {block} yet.")
                block_mappings[(x, y, z)] = finished.get_add_block(universal)

        for old, new in palette_mappings.items():
            chunk.blocks[chunk.blocks == old] = new
        for (x, y, z), new in block_mappings.items():
            chunk.blocks[x, y, z] = new
        return chunk, numpy.array(finished.blocks())

    def to_universal(
            self,
            chunk_version: Union[int, Tuple[int, int, int]],
            translation_manager: PyMCTranslate.TranslationManager,
            chunk: Chunk,
            palette: numpy.ndarray,
            callback: Callable,
            full_translate: bool
    ) -> Tuple[Chunk, numpy.ndarray]:
        """
        Translate an interface-specific chunk into the universal format.

        :param chunk_version: The version number (int or tuple) of the input chunk
        :param translation_manager: PyMCTranslate.TranslationManager used for the translation
        :param chunk: The chunk to translate.
        :param palette: The palette that the chunk's indices correspond to.
        :param callback: function callback to get a chunk's data
        :param full_translate: if true do a full translate. If false just unpack the palette (used in callback)
        :return: Chunk object in the universal format.
        """
        version = translation_manager.get_version(*self._translator_key(chunk_version))
        translator = version.get()
        palette = self._unpack_palette(version, palette)
        return self._translate(chunk, palette, callback, translator.to_universal, full_translate)

    def from_universal(
            self,
            max_world_version_number: Union[int, Tuple[int, int, int]],
            translation_manager: PyMCTranslate.TranslationManager,
            chunk: Chunk,
            palette: numpy.ndarray,
            callback: Union[Callable, None],
            full_translate: bool
    ) -> Tuple[Chunk, numpy.ndarray]:
        """
        Translate a universal chunk into the interface-specific format.

        :param max_world_version_number: The version number (int or tuple) of the max world version
        :param translation_manager: PyMCTranslate.TranslationManager used for the translation
        :param chunk: The chunk to translate.
        :param palette: The palette that the chunk's indices correspond to.
        :param callback: function callback to get a chunk's data
        :param full_translate: if true do a full translate. If false just pack the palette (used in callback)
        :return: Chunk object in the interface-specific format and palette.
        """
        version = translation_manager.get_version(*self._translator_key(max_world_version_number))
        translator = version.get()
        chunk, palette = self._translate(chunk, palette, callback, translator.from_universal, full_translate)
        palette = self._pack_palette(version, palette)
        return chunk, palette

    def _unpack_palette(
            self,
            version: Version,
            palette: numpy.ndarray
    ) -> numpy.ndarray:
        """
        Unpack the version-specific palette into the stringified version where needed.

        :return: The palette converted to block objects.
        """
        return palette

    def _pack_palette(
            self,
            version: Version,
            palette: numpy.ndarray
    ) -> numpy.ndarray:
        """
        Translate the list of block objects into a version-specific palette.
        :return: The palette converted into version-specific blocks (ie id, data tuples for 1.12)
        """
        return palette


if __name__ == "__main__":
    import time

    print(loader.get_all())
    time.sleep(1)
    loader.reload()
    print(loader.get_all())
