from __future__ import annotations

from amulet.world_interface.chunk.interfaces.anvil.anvil_1467_1_13.anvil_1467_interface import Anvil1467Interface


class Anvil1901Interface(Anvil1467Interface):
    def __init__(self):
        Anvil1467Interface.__init__(self)
        # self.features["status"] = "j13"  # TODO check this

        # isLightOn

        self.features["height_map"] = "C5|36LA"

        # lights
        # carving masks
        # heightmaps

    @staticmethod
    def minor_is_valid(key: int):
        return 1901 <= key < 2203


INTERFACE_CLASS = Anvil1901Interface
