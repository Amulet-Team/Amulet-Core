from __future__ import annotations

from typing import Union, Tuple

from amulet.world_interface.chunk.translators import Translator


class Bedrock_15_Translator(Translator):
    def _translator_key(
        self, version_number: Union[int, Tuple[int, int, int]]
    ) -> Tuple[str, Union[int, Tuple[int, int, int]]]:
        if isinstance(version_number, int):  # must be 15
            return "bedrock", (1, 11, 4)
        return "bedrock", version_number

    @staticmethod
    def is_valid(key):
        if key[0] != "leveldb":
            return False
        if key[1] != 15:
            return False
        return True


TRANSLATOR_CLASS = Bedrock_15_Translator
