from __future__ import annotations

import numpy

from typing import Tuple, Callable, Union

from amulet.api.chunk import Chunk
from amulet.api.block import Block
from amulet.world_interface.chunk.translators import Translator
import PyMCTranslate


class BaseBedrockTranslator(Translator):
    def _translator_key(
        self, version_number: Tuple[int, int, int]
    ) -> Tuple[str, Tuple[int, int, int]]:
        return "bedrock", version_number

    def to_universal(
        self,
        game_version: Tuple[int, int, int],
        translation_manager: PyMCTranslate.TranslationManager,
        chunk: Chunk,
        palette: numpy.ndarray,
        callback: Callable,
        full_translate: bool,
    ) -> Tuple[Chunk, numpy.ndarray]:
        # Bedrock does versioning by block rather than by chunk.
        # As such we can't just pass in a single translator.
        # It needs to be done dynamically.
        versions = {}

        def translate(
            block: Tuple[Union[Tuple[int, int, int], None], Block],
            get_block_callback: Callable = None
        ):
            game_version_, block = block
            if game_version_ is None:
                game_version_ = game_version
            version_key = self._translator_key(game_version_)
            translator = versions.setdefault(version_key, translation_manager.get_version(*version_key).get().to_universal)
            return translator(block, get_block_callback)

        version = translation_manager.get_version(*self._translator_key(game_version))
        palette = self._unpack_palette(version, palette)
        return self._translate(
            chunk, palette, callback, translate, full_translate
        )
