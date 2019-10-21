from __future__ import annotations

import numpy

from amulet.world_interface.translators import Translator

import PyMCTranslate


class Java_1_12_2_Translator(Translator):
    def _translator_key(self):
        return ("java", (1, 12, 2))

    def _unpack_palette(self, translation_manager: PyMCTranslate.TranslationManager, palette: numpy.ndarray):
        """
        Unpacks an int array of block ids and block data values [[1, 0], [2, 0]] into a numpy array of Block objects.
        :param translation_manager:
        :param palette:
        :return:
        """
        version = translation_manager.get_version(*self._translator_key())
        palette = numpy.array([version.ints_to_block(*entry) for entry in palette])
        return palette

    def _pack_palette(
            self,
            translation_manager: PyMCTranslate.TranslationManager,
            palette: numpy.ndarray
    ) -> numpy.ndarray:
        """
        Packs a numpy array of Block objects into an int array of block ids and block data values [[1, 0], [2, 0]].
        :param translation_manager:
        :param palette:
        :return:
        """
        version = translation_manager.get_version(*self._translator_key())
        palette = numpy.array([version.block_to_ints(entry) for entry in palette])
        return palette

    @staticmethod
    def is_valid(key):
        if key[0] != "anvil":
            return False
        if key[1] > 1343:
            return False
        return True


TRANSLATOR_CLASS = Java_1_12_2_Translator
