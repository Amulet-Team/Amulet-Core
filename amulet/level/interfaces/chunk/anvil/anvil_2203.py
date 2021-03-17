from __future__ import annotations

from .anvil_1912 import (
    Anvil1912Interface,
)


class Anvil2203Interface(Anvil1912Interface):
    def __init__(self):
        Anvil1912Interface.__init__(self)
        self.features["biomes"] = "1024IA"  # optional

    @staticmethod
    def minor_is_valid(key: int):
        return 2203 <= key < 2529


export = Anvil2203Interface
