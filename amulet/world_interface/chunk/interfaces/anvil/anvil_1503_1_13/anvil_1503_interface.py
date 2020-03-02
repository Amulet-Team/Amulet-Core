from __future__ import annotations

from amulet.world_interface.chunk.interfaces.anvil.anvil_1484_1_13.anvil_1484_interface import (
    Anvil1484Interface,
)


class Anvil1503Interface(Anvil1484Interface):
    def __init__(self):
        Anvil1484Interface.__init__(self)
        self.features["height_map"] = "C|36LA|V3"

    @staticmethod
    def minor_is_valid(key: int):
        return 1503 <= key < 1908


INTERFACE_CLASS = Anvil1503Interface
