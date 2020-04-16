from __future__ import annotations

from amulet.world_interface.chunk.interfaces.anvil.anvil_na.interface import (
    AnvilNAInterface,
)


class Anvil112Interface(AnvilNAInterface):
    def __init__(self):
        AnvilNAInterface.__init__(self)

    @staticmethod
    def minor_is_valid(key: int):
        return 0 <= key < 1444


INTERFACE_CLASS = Anvil112Interface
