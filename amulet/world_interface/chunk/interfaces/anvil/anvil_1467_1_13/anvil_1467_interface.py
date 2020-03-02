from __future__ import annotations

from amulet.world_interface.chunk.interfaces.anvil.anvil_1466_1_13.anvil_1466_interface import (
    Anvil1466Interface,
)


class Anvil1467Interface(Anvil1466Interface):
    def __init__(self):
        Anvil1466Interface.__init__(self)
        self.features["biomes"] = "256IA"

    @staticmethod
    def minor_is_valid(key: int):
        return 1467 <= key < 1484


INTERFACE_CLASS = Anvil1467Interface
