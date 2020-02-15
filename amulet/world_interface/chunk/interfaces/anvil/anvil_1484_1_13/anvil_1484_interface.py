from __future__ import annotations

from amulet.world_interface.chunk.interfaces.anvil.anvil_1467_1_13.anvil_1467_interface import (
    Anvil1467Interface,
)


class Anvil1484Interface(Anvil1467Interface):
    def __init__(self):
        Anvil1467Interface.__init__(self)
        self.features["height_map"] = "C|36LA|V2"

    @staticmethod
    def minor_is_valid(key: int):
        return 1484 <= key < 1503


INTERFACE_CLASS = Anvil1484Interface
