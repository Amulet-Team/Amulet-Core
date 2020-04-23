from __future__ import annotations

from amulet.world_interface.chunk.interfaces.anvil.anvil_1912_1_14.anvil_1912_interface import (
    Anvil1912Interface,
)


class Anvil2203Interface(Anvil1912Interface):
    def __init__(self):
        Anvil1912Interface.__init__(self)
        self.features["biomes"] = "1024IA"  # optional

    @staticmethod
    def minor_is_valid(key: int):
        return 2203 <= key < 2529


INTERFACE_CLASS = Anvil2203Interface
