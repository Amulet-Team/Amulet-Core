from __future__ import annotations

from amulet.world_interface.chunk.interfaces.anvil.anvil_1908_1_14.anvil_1908_interface import (
    Anvil1908Interface,
)


class Anvil1912Interface(Anvil1908Interface):
    def __init__(self):
        Anvil1908Interface.__init__(self)
        self.features["status"] = "j14"

    @staticmethod
    def minor_is_valid(key: int):
        return 1912 <= key < 2203


INTERFACE_CLASS = Anvil1912Interface
