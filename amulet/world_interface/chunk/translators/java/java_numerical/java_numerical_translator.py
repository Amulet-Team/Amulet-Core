from __future__ import annotations

from typing import Tuple, Union, TYPE_CHECKING
import numpy

from amulet.api.chunk import Chunk
from amulet.api.wrapper import Translator
from amulet.api.data_types import VersionIdentifierType, AnyNDArray, BlockNDArray
from amulet.api.registry import BlockManager

if TYPE_CHECKING:
    from PyMCTranslate import Version, TranslationManager


class JavaNumericalTranslator(Translator):
    def _translator_key(
        self, version_number: int
    ) -> Tuple[str, Union[int, Tuple[int, int, int]]]:
        return "java", version_number

    @staticmethod
    def _unpack_blocks(
        translation_manager: "TranslationManager",
        version_identifier: VersionIdentifierType,
        chunk: Chunk,
        block_palette: AnyNDArray,
    ):
        """
        Unpacks an int array of block ids and block data values [[1, 0], [2, 0]] into a numpy array of Block objects.
        :param version:
        :param block_palette:
        :return:
        """
        version = translation_manager.get_version(*version_identifier)
        chunk._block_palette = BlockManager(
            [version.block.ints_to_block(*entry) for entry in block_palette]
        )

    def _pack_block_palette(
        self, version: "Version", palette: BlockNDArray
    ) -> AnyNDArray:
        """
        Packs a numpy array of Block objects into an int array of block ids and block data values [[1, 0], [2, 0]].
        :param version:
        :param palette:
        :return:
        """
        palette = [version.block.block_to_ints(entry) for entry in palette]
        for index, value in enumerate(palette):
            if value is None:
                palette[index] = (
                    0,
                    0,
                )  # TODO: find some way for the user to specify this
        return numpy.array(palette)

    @staticmethod
    def is_valid(key):
        if key[0] != "java":
            return False
        if key[1] > 1343:
            return False
        return True


TRANSLATOR_CLASS = JavaNumericalTranslator
