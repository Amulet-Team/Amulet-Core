from __future__ import annotations

from amulet.world_interface.chunk.interfaces.anvil.anvil_1444_1_13.anvil_1444_1_13_interface import Anvil1444Interface


class Anvil1467Interface(Anvil1444Interface):
    def __init__(self):
        Anvil1444Interface.__init__(self)
        self.features["biomes"] = "256IA"

    @staticmethod
    def minor_is_valid(key: int):
        return 1467 <= key < 1901


INTERFACE_CLASS = Anvil1467Interface
