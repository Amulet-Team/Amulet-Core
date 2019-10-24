from __future__ import annotations

from typing import Tuple, Union
import numpy

from amulet.world_interface.chunk.translators import Translator

from PyMCTranslate.py3.translation_manager import Version


class JavaNumericalTranslator(Translator):
    def _translator_key(self, version_number: int) -> Tuple[str, Union[int, Tuple[int, int, int]]]:
        return "java", version_number

    def _unpack_palette(self, version: Version, palette: numpy.ndarray):
        """
        Unpacks an int array of block ids and block data values [[1, 0], [2, 0]] into a numpy array of Block objects.
        :param version:
        :param palette:
        :return:
        """
        palette = numpy.array([version.ints_to_block(*entry) for entry in palette])
        return palette

    def _pack_palette(
            self,
            version: Version,
            palette: numpy.ndarray
    ) -> numpy.ndarray:
        """
        Packs a numpy array of Block objects into an int array of block ids and block data values [[1, 0], [2, 0]].
        :param version:
        :param palette:
        :return:
        """
        palette = numpy.array([version.block_to_ints(entry) for entry in palette])
        return palette

    @staticmethod
    def is_valid(key):
        if key[0] != "anvil":
            return False
        if key[1] > 1343:
            return False
        return True


TRANSLATOR_CLASS = JavaNumericalTranslator
