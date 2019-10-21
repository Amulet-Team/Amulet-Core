from __future__ import annotations

import glob
import importlib
import json
import os
import numpy

from typing import Tuple, AbstractSet, Dict, Callable, Union

from amulet.api.errors import TranslatorLoaderNoneMatched
from ...api.block import BlockManager
from ...api.chunk import Chunk
import PyMCTranslate


_loaded_translators: Dict[str, Translator] = {}
_has_loaded_translators = False

SUPPORTED_TRANSLATOR_VERSION = 0
SUPPORTED_META_VERSION = 0

TRANSLATORS_DIRECTORY = os.path.dirname(__file__)


def _find_translators():
    global _has_loaded_translators

    directories = glob.iglob(os.path.join(TRANSLATORS_DIRECTORY, "*", ""))
    for d in directories:
        meta_path = os.path.join(d, "translator.meta")
        if not os.path.exists(meta_path):
            continue

        with open(meta_path) as fp:
            translator_info = json.load(fp)

        if translator_info["meta_version"] != SUPPORTED_META_VERSION:
            print(
                f'[Error] Couldn\'t enable translator located in "{d}" due to unsupported meta version'
            )
            continue

        if (
            translator_info["translator"]["translator_version"]
            != SUPPORTED_TRANSLATOR_VERSION
        ):
            print(
                f"[Error] Couldn't enable translator \"{translator_info['translator']['id']}\" due to unsupported translator version"
            )
            continue

        spec = importlib.util.spec_from_file_location(
            translator_info["translator"]["entry_point"],
            os.path.join(d, translator_info["translator"]["entry_point"] + ".py"),
        )
        modu = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modu)

        if not hasattr(modu, "TRANSLATOR_CLASS"):
            print(
                f"[Error] Translator \"{translator_info['translator']['id']}\" is missing the TRANSLATOR_CLASS attribute"
            )
            continue

        _loaded_translators[
            translator_info["translator"]["id"]
        ] = modu.TRANSLATOR_CLASS()

        if __debug__:
            print(
                f"[Debug] Enabled translator \"{translator_info['translator']['id']}\", version {translator_info['translator']['wrapper_version']}"
            )

    _has_loaded_translators = True


def reload():
    """Reloads all translators"""
    _loaded_translators.clear()
    _find_translators()


def get_all_loaded_translators() -> AbstractSet[str]:
    """
    :return: The identifiers of all loaded translators
    """
    if not _has_loaded_translators:
        _find_translators()
    return _loaded_translators.keys()


def get_translator(identifier: Tuple) -> Translator:
    """
    Gets the class for the translator with the given ``translator_id``

    :param identifier: The translator identifier for the desired loaded translator
    :return: The class for the translator
    """
    translator_id = _identify(identifier)
    return _loaded_translators[translator_id]


def _identify(identifier: Tuple) -> str:
    if not _has_loaded_translators:
        _find_translators()

    for translator_name, translator_instance in _loaded_translators.items():
        if translator_instance.is_valid(identifier):
            return translator_name

    raise TranslatorLoaderNoneMatched("Could not find a matching translator loader")


class Translator:
    # TODO: full_translate
    def to_universal(
            self,
            translation_manager: PyMCTranslate.TranslationManager,
            chunk: Chunk,
            palette: numpy.ndarray,
            callback: Callable,
            full_translate: bool
    ) -> Tuple[Chunk, BlockManager]:
        """
        Translate an interface-specific chunk into the universal format.

        :param chunk: The chunk to translate.
        :return: Chunk object in the universal format.
        """
        translator = translation_manager.get_sub_version(*self._translator_key())
        palette = self._translate_palette_to_universal(translation_manager, palette)

        todo = []
        finished = BlockManager()
        paletteMappings = {}

        for i, block in enumerate(palette):
            universal, entity, extra = translator.to_universal(block)
            if entity:
                print(f"Warning: not sure what to do with entity for {block} yet.")
            if extra and callback:
                todo.append(i)
                continue
            paletteMappings[i] = finished.get_add_block(universal)

        blockMappings = {}
        for index in todo:
            for x, y, z in zip(*numpy.where(chunk._blocks == index)):

                def get_block_at(pos):
                    nonlocal x, y, z, palette, chunk
                    dx, dy, dz = pos
                    dx += x
                    dy += y
                    dz += z
                    cx = dx // 16
                    cz = dz // 16
                    if cx == 0 and cz == 0:
                        return palette[chunk._blocks[dx % 16, dy, dz % 16]], None
                    chunk, palette = callback(cx, cz)
                    block = palette[chunk._blocks[dx % 16, dy, dz % 16]]
                    return translator.from_universal(block)[0], None

                block = palette[chunk._blocks[x, y, z]]
                universal, entity, extra = translator.to_universal(block, get_block_at)
                if entity:
                    print(f"Warning: not sure what to do with entity for {block} yet.")
                blockMappings[(x, y, z)] = finished.get_add_block(universal)

        for old, new in paletteMappings.items():
            chunk._blocks[chunk._blocks == old] = new
        for (x, y, z), new in blockMappings.items():
            chunk._blocks[x, y, z] = new
        return chunk, finished

    def _translator_key(self) -> Tuple[str, Tuple[int, int, int]]:
        """
        Return the version key for PyMCTranslate

        :return: The tuple version key for PyMCTranslate
        """
        raise NotImplementedError()

    def _translate_palette_to_universal(self, translation_manager: PyMCTranslate.TranslationManager, palette: numpy.ndarray) -> numpy.ndarray:
        """
        Translate the palette into a list of block objects.

        :return: The palette converted to block objects.
        """
        return palette

    def from_universal(
            self,
            translation_manager: PyMCTranslate.TranslationManager,
            chunk: Chunk,
            palette: numpy.ndarray,
            callback: Union[Callable, None],
            full_translate: bool
    ) -> Tuple[Chunk, numpy.ndarray]:
        """
        Translate a universal chunk into the interface-specific format.

        :param chunk: The chunk to translate.
        :param palette: The palette that the chunk's indicies correspond to.
        :return: Chunk object in the interface-specific format and palette.
        """
        raise NotImplementedError()

    def _translate_palette_from_universal(self, translation_manager: PyMCTranslate.TranslationManager, palette: BlockManager):
        """
        Translate the list of block objects into a version-specific palette.

        :return: The palette converted into version-specific blocks (ie id, data tuples for 1.12)
        """

    @staticmethod
    def is_valid(key: Tuple) -> bool:
        """
        Returns whether this translator is able to translate the chunk type with a given identifier key,
        generated by the decoder.

        :param key: The key who's decodability needs to be checked.
        :return: True if this translator is able to translate the chunk type associated with the key, False otherwise.
        """
        raise NotImplementedError()


if __name__ == "__main__":
    import time

    _find_translators()
    print(_loaded_translators)
    time.sleep(1)
    reload()
    print(_loaded_translators)
