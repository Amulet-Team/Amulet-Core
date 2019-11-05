from __future__ import annotations

from amulet.world_interface.chunk.translators.bedrock import BaseBedrockTranslator


class BedrockNumericalTranslator(BaseBedrockTranslator):
    @staticmethod
    def is_valid(key):
        if key[0] != "leveldb":
            return False
        if not key[1] < (1, 2, 13):
            return False
        return True



TRANSLATOR_CLASS = BedrockNumericalTranslator
