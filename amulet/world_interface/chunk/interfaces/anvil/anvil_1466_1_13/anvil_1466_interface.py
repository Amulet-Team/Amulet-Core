from __future__ import annotations

from amulet.world_interface.chunk.interfaces.anvil.anvil_1444_1_13.anvil_1444_1_13_interface import (
    Anvil1444Interface,
)


class Anvil1466Interface(Anvil1444Interface):
    def __init__(self):
        Anvil1444Interface.__init__(self)
        self.features["height_map"] = "C|36LA|V1"

    @staticmethod
    def minor_is_valid(key: int):
        return 1466 <= key < 1467


INTERFACE_CLASS = Anvil1466Interface
