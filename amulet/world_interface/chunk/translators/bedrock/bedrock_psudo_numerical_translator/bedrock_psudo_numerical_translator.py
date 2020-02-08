from __future__ import annotations

import numpy
from typing import Tuple, Union

from amulet.world_interface.chunk.translators.bedrock import BaseBedrockTranslator
from amulet.api.block import Block

from PyMCTranslate.py3.translation_manager import Version


class BedrockPsudoNumericalTranslator(BaseBedrockTranslator):
    @staticmethod
    def is_valid(key):
        if key[0] != "bedrock":
            return False
        if not (1, 2, 13) <= key[1] < (1, 13, 0):
            return False
        return True

    def _pack_palette(self, version: Version, palette: numpy.ndarray) -> numpy.ndarray:
        """
        Packs a numpy array of Block objects into an object array of containing block ids and block data values.
        :param version:
        :param palette:
        :return:
        """
        palette_ = numpy.empty(len(palette), dtype=object)
        for palette_index, block in enumerate(palette):
            block: Block
            # TODO: perhaps check that property 'block_data' exists and str.isnumeric user interaction if not
            palette_[palette_index] = ((None, block.base_block),) + tuple(
                (None, extra_block) for extra_block in block.extra_blocks
            )

        return palette_


TRANSLATOR_CLASS = BedrockPsudoNumericalTranslator
