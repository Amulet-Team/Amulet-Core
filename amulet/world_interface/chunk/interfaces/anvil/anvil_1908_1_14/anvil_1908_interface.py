from __future__ import annotations

from amulet.world_interface.chunk.interfaces.anvil.anvil_1503_1_13.anvil_1503_interface import (
    Anvil1503Interface,
)


class Anvil1908Interface(Anvil1503Interface):
    def __init__(self):
        Anvil1503Interface.__init__(self)
        self.features["height_map"] = "C|36LA|V4"

    @staticmethod
    def minor_is_valid(key: int):
        return 1908 <= key < 1912


INTERFACE_CLASS = Anvil1908Interface
