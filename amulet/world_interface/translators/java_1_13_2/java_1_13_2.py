from __future__ import annotations

from amulet.world_interface.translators.translator import Translator


class Java_1_13_2_Translator(Translator):
    def _translator_key(self):
        return ("java", (1, 13, 2))

    @staticmethod
    def is_valid(key):
        if key[0] != "anvil":
            return False
        if key[1] < 1444:
            return False
        return True


TRANSLATOR_CLASS = Java_1_13_2_Translator
