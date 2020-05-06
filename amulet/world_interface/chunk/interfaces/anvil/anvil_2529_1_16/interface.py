from __future__ import annotations

from amulet.world_interface.chunk.interfaces.anvil.anvil_2203_1_15.anvil_2203_interface import (
    Anvil2203Interface,
)


class Anvil2529Interface(Anvil2203Interface):
    def __init__(self):
        super().__init__()
        self.features["long_array_format"] = "1.16"

    @staticmethod
    def minor_is_valid(key: int):
        return 2529 <= key < 3000


INTERFACE_CLASS = Anvil2529Interface
