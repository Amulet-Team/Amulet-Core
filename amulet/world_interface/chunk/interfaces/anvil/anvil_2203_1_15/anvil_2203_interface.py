from __future__ import annotations

from amulet.world_interface.chunk.interfaces.anvil.anvil_1901_1_14.anvil_1901_interface import (
    Anvil1901Interface
)


class Anvil2203Interface(Anvil1901Interface):
    def __init__(self):
        Anvil1901Interface.__init__(self)

        # self.features["status"] = "j13"  # TODO check this

        self.features["biomes"] = "1024IA"  # optional

    @staticmethod
    def minor_is_valid(key: int):
        return 2203 <= key < 2500


INTERFACE_CLASS = Anvil2203Interface
