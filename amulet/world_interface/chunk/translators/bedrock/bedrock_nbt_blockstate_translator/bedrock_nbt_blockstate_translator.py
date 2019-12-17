from __future__ import annotations

import numpy
from typing import Tuple, Union

from amulet.world_interface.chunk.translators.bedrock import BaseBedrockTranslator
from amulet.api.block import Block

from PyMCTranslate.py3.translation_manager import Version


class BedrockNBTBlockstateTranslator(BaseBedrockTranslator):
    @staticmethod
    def is_valid(key):
        if key[0] != "bedrock":
            return False
        if not (1, 13, 0) <= key[1]:
            return False
        return True

    def _unpack_palette(self, version: Version, palette: numpy.ndarray):
        """
        Unpacks an object array of block data into a numpy object array containing Block objects.
        :param version:
        :param palette:
        :type palette: numpy.ndarray[
            Tuple[
                Union[
                    Tuple[None, Tuple[int, int]],
                    Tuple[None, Block],
                    Tuple[Tuple[int, int, int, int], Block]
                ], ...
            ]
        ]
        :return:
        """
        palette_ = numpy.empty(len(palette), dtype=object)
        for palette_index, entry in enumerate(palette):
            entry: Tuple[
                Union[
                    Tuple[None, Tuple[int, int]],
                    Tuple[None, Block],
                    Tuple[Tuple[int, int, int, int], Block],
                ],
                ...,
            ]
            palette_[palette_index] = tuple(
                (block[0], version.ints_to_block(*block[1]))
                if isinstance(block[1], tuple)
                else block
                for block in entry
            )
        return palette_

    def _pack_palette(self, version: Version, palette: numpy.ndarray) -> numpy.ndarray:
        """
        Packs a numpy array of Block objects into an object array of containing block ids and block data values.
        :param version:
        :param palette:
        :return:
        """
        version_number = version.version_number
        if len(version_number) > 4:
            version_number = version_number[:4]
        elif len(version_number) < 4:
            version_number = version_number + (0,) * (4 - len(version_number))

        palette_ = numpy.empty(len(palette), dtype=object)
        for palette_index, block in enumerate(palette):
            block: Block
            # TODO: perhaps check that all properties are NBT objects user interaction if not
            palette_[palette_index] = ((version_number, block.base_block),) + tuple(
                (version_number, extra_block) for extra_block in block.extra_blocks
            )

        return palette_


TRANSLATOR_CLASS = BedrockNBTBlockstateTranslator
