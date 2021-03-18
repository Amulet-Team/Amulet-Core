from __future__ import annotations

from .anvil_1934 import (
    Anvil1934Interface,
)


class Anvil2203Interface(Anvil1934Interface):
    def __init__(self):
        Anvil1934Interface.__init__(self)
        self.features["biomes"] = "1024IA"  # optional

    @staticmethod
    def minor_is_valid(key: int):
        return 2203 <= key < 2529


export = Anvil2203Interface
