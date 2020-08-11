from __future__ import annotations

import numpy
from typing import TYPE_CHECKING

from amulet.world_interface.chunk.translators.bedrock import BaseBedrockTranslator
from amulet.api.data_types import BlockNDArray, AnyNDArray

if TYPE_CHECKING:
    from amulet.api.block import Block
    from PyMCTranslate import Version


class BedrockPsudoNumericalTranslator(BaseBedrockTranslator):
    @staticmethod
    def is_valid(key):
        if key[0] != "bedrock":
            return False
        if not (1, 2, 13) <= key[1] < (1, 13, 0):
            return False
        return True

    def _pack_block_palette(
        self, version: "Version", palette: BlockNDArray
    ) -> AnyNDArray:
        """
        Packs a numpy array of Block objects into an object array containing one pair of version number and Block objects.
        :param version:
        :param palette:
        :return: numpy.ndarray[Tuple[Tuple[Optional[VersionNumber], Block]]]
        """
        palette_ = numpy.empty(len(palette), dtype=object)
        for palette_index, block in enumerate(palette):
            block: "Block"
            # TODO: perhaps check that property 'block_data' exists and is TAG_Int user interaction if not
            palette_[palette_index] = tuple((None, b) for b in block.block_tuple)

        return palette_


TRANSLATOR_CLASS = BedrockPsudoNumericalTranslator
