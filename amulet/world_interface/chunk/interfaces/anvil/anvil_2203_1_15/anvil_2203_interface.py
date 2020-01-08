from __future__ import annotations

from ..anvil_1908_1_14.anvil_1908_interface import Anvil1908Interface


class Anvil2203Interface(Anvil1908Interface):
    def __init__(self):
        Anvil1908Interface.__init__(self)

        # self.features["status"] = "j13"  # TODO check this

        self.features["biomes"] = "1024IA"  # optional

    @staticmethod
    def minor_is_valid(key: int):
        return 2203 <= key < 2500


INTERFACE_CLASS = Anvil2203Interface
