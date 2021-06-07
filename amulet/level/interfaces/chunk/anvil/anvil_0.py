from __future__ import annotations

from .anvil_na import (
    AnvilNAInterface,
)


class Anvil112Interface(AnvilNAInterface):
    @staticmethod
    def minor_is_valid(key: int):
        return 0 <= key < 1444


export = Anvil112Interface
