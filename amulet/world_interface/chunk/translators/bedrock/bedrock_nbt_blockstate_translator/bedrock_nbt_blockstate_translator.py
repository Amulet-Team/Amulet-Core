from __future__ import annotations

import numpy
from typing import TYPE_CHECKING

from amulet.world_interface.chunk.translators.bedrock import BaseBedrockTranslator
from amulet.api.data_types import BlockNDArray, AnyNDArray
from amulet.api.block import Block

if TYPE_CHECKING:
    from PyMCTranslate import Version


class BedrockNBTBlockstateTranslator(BaseBedrockTranslator):
    @staticmethod
    def is_valid(key):
        if key[0] != "bedrock":
            return False
        if not (1, 13, 0) <= key[1]:
            return False
        return True

    def _pack_block_palette(
        self, version: "Version", palette: BlockNDArray
    ) -> AnyNDArray:
        """
        Packs a numpy array of Block objects into an object array containing one more more pairs of version number and Block objects.
        :param version:
        :param palette:
        :return: numpy.ndarray[Tuple[Tuple[Optional[VersionNumber], Block], ...]]
        """
        palette_ = numpy.empty(len(palette), dtype=object)
        for palette_index, block in enumerate(palette):
            block: "Block"
            # TODO: perhaps check that all properties are NBT objects user interaction if not
            blocks = []
            for b in block.block_tuple:
                if "__version__" in b.properties:
                    properties = b.properties
                    version_number = properties.pop("__version__").value
                    b = Block(b.namespace, b.base_name, properties, b.extra_blocks)
                else:
                    version_number = None
                blocks.append((version_number, b))
            palette_[palette_index] = tuple(blocks)

        return palette_


TRANSLATOR_CLASS = BedrockNBTBlockstateTranslator
