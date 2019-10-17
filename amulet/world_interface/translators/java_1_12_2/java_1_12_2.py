from __future__ import annotations

from amulet.world_interface.translators import Translator


class Java_1_12_2_Translator(Translator):
    def _translator_key(self):
        return ("java", (1, 12, 2))

    def _translate_palette(self, palette):
        version = self.translation_manager.get_version(*self._translator_key())
        palette = [version.ints_to_block(*entry) for entry in palette]
        return palette

    def from_universal(self, chunk):
        raise NotImplementedError()

    @staticmethod
    def is_valid(key):
        if key[0] != "anvil":
            return False
        if key[1] > 1343:
            return False
        return True


TRANSLATOR_CLASS = Java_1_12_2_Translator
