from __future__ import annotations

from amulet.world_interface.translators import Translator


class Bedrock_1_11_4_Translator(Translator):
    def _translator_key(self):
        return ("bedrock", (1, 11, 4))

    @staticmethod
    def is_valid(key):
        if key[0] != "leveldb":
            return False
        if key[1] != 15:
            return False
        return True


TRANSLATOR_CLASS = Bedrock_1_11_4_Translator
